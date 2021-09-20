import datetime
import json


class BasePush:
    def __init__(self, push_info):
        self.push_info = push_info

    def parse_push_info(self,
                        push_date_format,
                        simple_success_info_format,
                        errmsg_info_format,
                        details_push_flag=False,
                        details_push_format=None,
                        copy_right=False,
                        copy_right_delimiter="<br>"):
        utc8_time = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
        push_list = [
            push_date_format.format(utc8_time.strftime("%Y-%m-%d %H:%M:%S %p"))
        ]
        for check_info in self.push_info:
            # 打卡成功推送信息
            if check_info["status"]:

                name = check_info["post_dict"].get("username")
                if not name:
                    name = check_info["post_dict"]["name"]

                # 推送打卡详情
                if details_push_flag:
                    # 推送成功数据
                    push_list.append(details_push_format.format(
                        name, check_info["type"], check_info['res'],
                        json.dumps(check_info['check_json'], sort_keys=True, indent=4, ensure_ascii=False),
                        json.dumps(check_info['post_dict']['updatainfo_detail'], sort_keys=True, indent=4,
                                   ensure_ascii=False)
                    ))
                    # 生成表格
                    # push_list.append(
                    #     "\n".join(
                    #         [
                    #             f"| {i['description']} | {i['value']} |"
                    #             for i in check_info["post_dict"]["checkbox"]
                    #         ]) + "------"
                    # )
                else:
                    push_list.append(
                        simple_success_info_format.format(
                            name, check_info["type"], check_info["res"]
                        )
                    )
            # 打卡失败推送消息
            else:
                push_list.append(errmsg_info_format.format(check_info["errmsg"]))
        if copy_right:
            push_list.append(
                f"""{copy_right_delimiter}
感谢使用本脚本，本脚本仅供交流学习{copy_right_delimiter}
希望大家珍惜校园生活，在校好好学习（不只是书本，是成长）{copy_right_delimiter}
脚本地址：https://github.com/ReaJason/17wanxiaoCheckin
"""
            )
        return "\n".join(push_list)

    def push(self):
        pass
