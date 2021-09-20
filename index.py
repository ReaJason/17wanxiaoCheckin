import os
from utils.config import load_config
from core import UserInfo, HealthyTwoCheck, HealthyOneCheck, CampusCheck, info_push


def check_in(user):
    check_dict_list = []
    # 获取个人信息
    user_info_result = UserInfo(user["phone"], user["password"], user["device_id"]).get_user_info()
    if not user_info_result["status"]:
        check_dict_list.append(user_info_result)
        return check_dict_list

    # 开始打卡
    healthy1_check_config = user.get("healthy_checkin").get("one_check")
    healthy2_check_config = user.get("healthy_checkin").get("two_check")
    campus_check_config = user.get("campus_checkin")

    # 第一类健康打卡
    if healthy1_check_config and healthy1_check_config["enable"]:
        check_dict_list.append(
            HealthyOneCheck(
                user_info_result["user_info"], healthy1_check_config["post_json"]
            ).check_in()
        )
    # 第二类健康打卡
    if healthy2_check_config and healthy2_check_config["enable"]:
        check_dict_list.append(
            HealthyTwoCheck(
                user_info_result["user_info"], healthy2_check_config["post_json"]
            ).check_in()
        )
    # 校内打卡
    if campus_check_config and campus_check_config["enable"]:
        check_dict_list.extend(
            CampusCheck(
                user_info_result["user_info"], campus_check_config["post_json"]
            ).check_in()
        )
    return check_dict_list


def main_handler(**kwargs):
    # 推送数据
    raw_info = []

    # 加载用户配置文件
    user_config_dict = load_config(kwargs["user_config_path"])
    for user_config in user_config_dict:
        if not user_config["phone"]:
            continue
        # 单人打卡
        check_dict = check_in(user_config)
        # 单人推送
        info_push(user_config["push"], check_dict)
        raw_info.extend(check_dict)

    # 统一推送
    all_push_config = load_config(kwargs["push_config_path"])
    info_push(all_push_config, raw_info)


if __name__ == "__main__":
    user_config_path = os.path.join(os.path.dirname(__file__), "conf", "user.json")
    push_config_path = os.path.join(os.path.dirname(__file__), "conf", "push.json")
    main_handler(user_config_path=user_config_path, push_config_path=push_config_path)
