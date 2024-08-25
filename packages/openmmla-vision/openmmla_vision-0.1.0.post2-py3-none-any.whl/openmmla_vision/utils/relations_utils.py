import numpy as np


def is_tag_looking_at_another(tag1, tag2, angle_threshold, distance_threshold):
    """Check if tag1 is looking at tag2 considering their orientation and distance."""
    if isinstance(tag1, list):
        distance = np.linalg.norm(np.array(tag1[1]).ravel() - np.array(tag2[1]).ravel())
    else:
        distance = np.linalg.norm(tag1.pose_t.ravel() - tag2.pose_t.ravel())
    if distance > distance_threshold:
        return False

    normal1, _ = get_outward_normal(tag1)
    vector_from_tag2_to_tag1 = unit_vector_from_tag_to_tag(tag2, tag1)
    score = np.dot(normal1, vector_from_tag2_to_tag1)

    return score < angle_threshold


def get_outward_normal(tag):
    """Get the normal vector of the tag which perpendicular to the surface"""
    if isinstance(tag, list):  # for tag data [rotations, translations]
        normal = np.dot(np.array(tag[0]), np.array([0, 0, 1])).ravel()
        normal = -normal
        tag = None
    # for tag object
    else:
        normal = np.dot(tag.pose_R, np.array([0, 0, 1])).ravel()
        if np.dot(normal, tag.pose_t.ravel()) < 0:
            tag.pose_R[:, 2] = -tag.pose_R[:, 2]  # Flip the sign of the third column of the rotation matrix
        else:
            normal = -normal

    return normal, tag


def unit_vector_from_tag_to_tag(source_tag, target_tag):
    """Return the unit vector pointing from the source tag to the target tag"""
    if isinstance(source_tag, list):
        direction = np.array(target_tag[1]).ravel() - np.array(source_tag[1]).ravel()
    else:
        direction = target_tag.pose_t.ravel() - source_tag.pose_t.ravel()

    return direction / np.linalg.norm(direction)


def is_tag_looking_at_another_2d(tag1, tag2, angle_threshold, distance_threshold):
    """Check if tag1 is looking at tag2 considering their orientation and distance on the x-z plane."""
    if isinstance(tag1, list):
        distance = np.linalg.norm(np.array([tag1[1][0], tag1[1][2]]) - np.array([tag2[1][0], tag2[1][2]]))
    else:
        distance = np.linalg.norm(
            np.array([tag1.pose_t[0], tag1.pose_t[2]]) - np.array([tag2.pose_t[0], tag2.pose_t[2]]))
    # print(f"distance: {distance}")

    if distance > distance_threshold:
        return False

    normal1, _ = get_outward_normal_2d(tag1)
    vector_from_tag2_to_tag1 = unit_vector_from_tag_to_tag_2d(tag2, tag1)
    score = np.dot(normal1, vector_from_tag2_to_tag1)

    return score < angle_threshold


def get_outward_normal_2d(tag):
    """Get the normal vector of the tag which is perpendicular to the surface and project it onto the x-z plane."""
    if isinstance(tag, list):  # for tag data [rotations, translations] in synchronizer
        normal = np.dot(np.array(tag[0]), np.array([0, 0, 1])).ravel()
        normal = -normal
        tag = None
    else:  # for tag object in video base
        normal = np.dot(tag.pose_R, np.array([0, 0, 1])).ravel()
        if np.dot(normal, tag.pose_t.ravel()) < 0:
            tag.pose_R[:, 2] = -tag.pose_R[:, 2]  # Flip the sign of the third column of the rotation matrix
        else:
            normal = -normal

    normal_xz = np.array([normal[0], 0, normal[2]])  # Project onto x-z plane
    normal_xz /= np.linalg.norm(normal_xz)  # Normalize

    return normal_xz, tag


def unit_vector_from_tag_to_tag_2d(source_tag, target_tag):
    """Return the unit vector pointing from the source tag to the target tag on the x-z plane"""
    if isinstance(source_tag, list):
        direction = np.array(target_tag[1]).ravel() - np.array(source_tag[1]).ravel()
    else:
        direction = target_tag.pose_t.ravel() - source_tag.pose_t.ravel()
    direction_xz = np.array([direction[0], 0, direction[2]])  # Project onto x-z plane

    return direction_xz / np.linalg.norm(direction_xz)
