from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks


# dictionary of joint angles
# joint name: (min_angle, max_angle, minimum time from 0 to min or max)":
joints_dic = {
    "body.head.yaw": (-0.874, 0.874, 600),  # 0.3
    "body.head.roll": (-0.174, 0.174, 400),  # 0.2
    "body.head.pitch": (-0.174, 0.174, 400),  # 0.2
    "body.arms.right.upper.pitch": (-2.59, 1.59, 1800),  # 0.8
    "body.arms.right.lower.roll": (-1.74, 0.000064, 1200),  # 0.6
    "body.arms.left.upper.pitch": (-2.59, 1.59, 1600),  # 0.8
    "body.arms.left.lower.roll": (-1.74, 0.000064, 1200),  # 0.6
    "body.torso.yaw": (-0.874, 0.874, 1000),  # 0.5
    "body.legs.right.upper.pitch": (
        -1.74,
        1.74,
        1600,
    ),  # 0.8 + add warning about falling somehow
    "body.legs.right.lower.pitch": (
        -1.74,
        1.74,
        1200,
    ),  # 0.6 + add warning about falling somehow
    "body.legs.right.foot.roll": (
        -0.849,
        0.249,
        1000,
    ),  # 0.5 + add warning about falling somehow
    "body.legs.left.upper.pitch": (
        -1.74,
        1.74,
        1600,
    ),  # 0.8 + add warning about falling somehow
    "body.legs.left.lower.pitch": (
        -1.74,
        1.74,
        1200,
    ),  # 0.6 + add warning about falling somehow
    "body.legs.left.foot.roll": (
        -0.849,
        0.249,
        1000,
    ),  # 0.5 + add warning about falling somehow
}


def check_angle_set_value(frame_joints_dic):
    for joint in frame_joints_dic:
        if not joint in joints_dic:
            raise ValueError(joint + " is not a valid joint name")
        else:
            if (
                not joints_dic[joint][0]
                <= frame_joints_dic[joint]
                <= joints_dic[joint][1]
            ):
                raise ValueError(
                    "The angle selected for joint " + joint + " is out of bounds"
                )


def calculate_required_time(current_pos, target_pos, min_angle, max_angle, min_time):
    # calculate the total range of motion
    total_range = abs(max_angle - min_angle)

    # calculate the movement range required
    movement_range = abs(target_pos - current_pos)

    # calculate the proportional time
    proportional_time = (movement_range / total_range) * min_time

    return proportional_time


# the minimum time between any movements is proportional to the angle of movement
@inlineCallbacks
def perform_movement(
    session, frames, mode="linear", sync=True, force=False
):
    """
    This function performs a movement with the robot's joints. The time of each frame is calculated based on the proportional time of the movement.

    Args:
                session (Component): The session object.
                frames (list): A list of dictionaries with the time and data of the joints to be moved.
                mode (str): The mode of the movement. Choose one of the following: "linear", "last", "none".
                sync (bool): A flag to synchronize the movement of the joints.
                force (bool): A flag to force the movement of the joints.

        Returns:
                None
    """
    if not isinstance(frames, list) and all(isinstance(item, dict) for item in frames):
        raise TypeError(
            'frames is not a list of tuples, it needs to follow the structure [{"time": (int), "data": {name_joints (string): position_joint (float), ...}}'
        )

    if not isinstance(mode, str):
        raise TypeError(
            'mode is not a string, choose one of the following "linear", "last", "none"'
        )

    if not isinstance(sync, bool):
        raise TypeError(
            "sync is not a boolean, choose one of the following True, False"
        )

    if not isinstance(force, bool):
        raise TypeError(
            "force is not a boolean, choose one of the following True, False"
        )

        # check the joints and angles of the first frame
    check_angle_set_value(frames[0]["data"])

    # get the joints angle at this time
    current_position = yield session.call("rom.sensor.proprio.read")
    # print(current_position[0]["data"])

    # check the time set of the first frame
    for joint, target_position in frames[0]["data"].items():
        minimum_required_time = calculate_required_time(
            current_position[0]["data"][joint],
            target_position,
            joints_dic[joint][0],
            joints_dic[joint][1],
            joints_dic[joint][2],
        )

        minimum_required_time = round(minimum_required_time, 2)
        print(minimum_required_time)
        if frames[0]["time"] == None or minimum_required_time > frames[0]["time"]:
            print(
                "The time of frame 0 was changed from "
                + str(frames[0]["time"])
                + " to "
                + str(minimum_required_time)
            )
            frames[0]["time"] = minimum_required_time

    for idx in range(len(frames) - 1):
        frame1 = frames[idx]
        frame2 = frames[idx + 1]

        for joint, target_position in frame2["data"].items():
            minimum_required_time = calculate_required_time(
                frame1["data"][joint],
                target_position,
                joints_dic[joint][0],
                joints_dic[joint][1],
                joints_dic[joint][2],
            )
            minimum_required_time = round(minimum_required_time, 2)
        if frame2["time"] == None or minimum_required_time > frame2["time"]:
            print(
                "The time of frame "
                + str(idx + 1)
                + " was changed from "
                + str(frame2["time"])
                + " to "
                + str(minimum_required_time)
            )
            frame2["time"] = minimum_required_time

    session.call(
        "rom.actuator.motor.write", frames=frames, mode=mode, sync=sync, force=True
    )
