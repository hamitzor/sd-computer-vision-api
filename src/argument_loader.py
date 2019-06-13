import argparse

arguments = (
    ("-dbh", "--mongodb-host",  "MongoDB host"),
    ("-dbu", "--mongodb-user",  "MongoDB username"),
    ("-dbp", "--mongodb-password",  "MongoDB password"),
)

"""
    ("-c", "--config",  "path to yolo config file"),
    ("-w", "--weights",  "path to yolo weights file"),
    ("-cl", "--classes",  "path to file containing class names"),
    ("-id", "--video-id",  "id of the video that is going to be processed"),
    """

argparse = argparse.ArgumentParser()

for argument in arguments:
    argparse.add_argument(argument[0], argument[1], required=True, help=argument[2])

args = argparse.parse_args()
