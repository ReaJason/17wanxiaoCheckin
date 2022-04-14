from api.campus_check import get_id_list_v1, get_id_list_v2, get_customer_type_id, get_campus_check_post, \
    campus_check_in
from api.healthy1_check import get_healthy1_check_post_json, healthy1_check_in
from api.healthy2_check import get_healthy2_check_posh_json, healthy2_check_in
from api.user_info import get_user_info
from api.wanxiao_push import wanxiao_qmsg_push, wanxiao_server_push, wanxiao_email_push, wanxiao_pipe_push, \
    wanxiao_wechat_enterprise_push, wanxiao_bark_push
from api.ykt_score import get_score_list, get_active_score, get_task_list, get_article_id, get_all_score, \
    get_article_score, get_class_score, ykt_check_in