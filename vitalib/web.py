import re

@staticmethod
def is_mobile(user_agent):
    mobile_agent_re = re.compile(
        r".*(iphone|mobile|androidtouch|blackberry|nokia|phone|palm|windows ce|windows phone|opera mini|operamobile|nokia|samsung|htc|lg|fennec|symbian|maemo|webos|bolt|docomo|up.browser|tablet|pad|kindle|silk|playbook).*",
        re.IGNORECASE,
    )
    return bool(mobile_agent_re.match(user_agent))