from enum import Enum


class WanXiaoServiceUrlEnum(Enum):
    EPMPICS_URL = "https://reportedh5.17wanxiao.com/sass/api/epmpics"
    GET_USER_INFO_URL = "https://reportedh5.17wanxiao.com/api/clock/school/getUserInfo"
    GET_CAMPUS_CHECK_CUSTOM_ID_URL = (
        "https://reportedh5.17wanxiao.com/api/clock/school/childApps"
    )
    GET_CAMPUS_CHECK_ID_LIST1_URL = (
        "https://reportedh5.17wanxiao.com/api/clock/school/rules"
    )
    GET_CAMPUS_CHECK_ID_LIST2_URL = (
        "https://reportedh5.17wanxiao.com/api/clock/school/childApps"
    )
    GET_HEALTHY2_CHECK_DICT_URL = "https://reportedh5.17wanxiao.com/api/reported/recall"
    HEALTHY2_CHECK_IN_URL = "https://reportedh5.17wanxiao.com/api/reported/receive"
