def canonicalize_name(name):
    """
    Put name in canonical form. Double slashes '//' are removed and
    name is returned without any trailing slash, e.g. /foo/bar
    @param name: ROS name
    @type  name: str
    """

    # Straight up copied from here: https://docs.ros.org/en/melodic/api/rospy/html/rospy.names-pysrc.html

    SEP = '/'

    if not name or name == SEP:
        return name
    elif name[0] == SEP:
        return '/' + '/'.join([x for x in name.split(SEP) if x])
    else:
        return '/'.join([x for x in name.split(SEP) if x])
