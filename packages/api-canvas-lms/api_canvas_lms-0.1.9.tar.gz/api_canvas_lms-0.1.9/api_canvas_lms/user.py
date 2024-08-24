""" 
Programa : User module for Canvas
Fecha Creacion : 05/08/2024
Fecha Update : None
Version : 1.0.0
Actualizacion : None
Author : Jaime Gomez
"""

import logging
from .base import BaseCanvas

# Create a logger for this module
logger = logging.getLogger(__name__)

class User(BaseCanvas):

    def __init__(self, user_id, access_token):
        super().__init__(access_token)
        # 
        self.user_id = str(user_id)
        # CONNECTOR
        self.url_users_enrollments   = '<path>/users/<teacher_id>/enrollments'

    def get_courses(self, params = None):
        url = self.url_users_enrollments
        url = url.replace('<teacher_id>', self.user_id)
        return self.get_all_pages(url,params)


'''
curl '
https://tecsup.instructure.com/api/v1/accounts/
788/courses?
sort=sis_course_id &
order=asc&search_by=course &
include%5B%5D=total_students &
include%5B%5D=active_teachers &
include%5B%5D=subaccount &
include%5B%5D=term &
include%5B%5D=concluded &
include%5B%5D=ui_invoked &
teacher_limit=25
&per_page=15&
no_avatar_fallback=1' \
  -H 'accept: application/json, text/javascript, application/json+canvas-string-ids, */*; q=0.01' \
  -H 'accept-language: en-GB,en-US;q=0.9,en;q=0.8' \
  -H 'baggage: sentry-environment=Production,sentry-release=canvas-lms%4020240731.236,sentry-public_key=355a1d96717e4038ac25aa852fa79a8f,sentry-trace_id=2347c402bb804e2b8ea585c90eea1e26,sentry-sample_rate=0.005,sentry-sampled=false' \
  -H 'cookie: _mkto_trk=id:449-BVJ-543&token:_mch-instructure.com-1680397369957-58870; cb_user_id=null; cb_group_id=null; lo-uid=ed70c3d3-1699834512974-54cab43c05232932; lo-visits=1; __utmzz=utmcsr=google|utmcmd=organic|utmccn=(not set)|utmctr=(not provided); _ga=GA1.1.2008050582.1680397370; _fbp=fb.1.1713384110420.1569467605; __utmzzses=1; _hp2_props.3295960117=%7B%22Region%22%3A%22Americas-North%20America%22%2C%22Page%20Node%22%3A%2224569%22%2C%22Page%20Group%22%3A%22Product%22%2C%22Page%20Type%22%3A%22Login%22%7D; _hp2_props.3001039959=%7B%22Base.appName%22%3A%22Canvas%22%7D; _hp2_id.3001039959=%7B%22userId%22%3A%22573430259265655%22%2C%22pageviewId%22%3A%221889506941661303%22%2C%22sessionId%22%3A%226207602181576955%22%2C%22identity%22%3A%22uu-2-0068b86a00b5fb00d5476a54fa940f2fc3a5e553e2bdff35e092d65d1c7d8f6a-ff2e5780-fa5b-012d-f7b3-123135003972%22%2C%22trackerVersion%22%3A%224.0%22%2C%22identityField%22%3Anull%2C%22isIdentified%22%3A1%2C%22oldIdentity%22%3Anull%7D; _gcl_au=1.1.2063621924.1721965112; _ga_75H5134F9J=GS1.1.1721965112.10.0.1721965112.60.0.0; _hp2_id.3295960117=%7B%22userId%22%3A%224367258233974184%22%2C%22pageviewId%22%3A%223733684909282361%22%2C%22sessionId%22%3A%221980473725624463%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D; _uetvid=b68d99d081b911ee8f4d19ea976a0bbb; _clck=1g3hj92%7C2%7Cfns%7C0%7C1412; log_session_id=c91079a675599374e163a029d6b489b4; _legacy_normandy_session=R9cFJ0B8fw2kGghnM3hNVw+3mycko-nCqgy8W7XB2S1B-lsOjJEDPiMcF9gfUUwG_ZSYjTmHRwLDnGnZNNjH8sKeGO4MdElDodJnh6jrfuC6hwUdcducIJv-vZzk1vL-8q9pMKpW4D3sk-3T9BSgp8HtwPDyU1Z3KnVt8t7s86chnlGE7bnXI_uIVzKgU9sgo8hu0Gk9McrVo0i9pc4JzxLLqaj6fZ9oKDlc1YRQJ0ULQqLP4yMoHvF7bp-gohkCa4LAAlDY_bxwuou0anss_PQ7qugutoypqVGSSD006hFASi5ytVuzIwHNzjs_iTRE3jov8Ev-woaKH-7F2uzurpBtX2tPm2y3FYie4rY1fyM38kXVt7R5J1FAt7Px4reGoSfwMBuwjV96yKnha3SEkJhH0ctWKDdzpntWWoBqUa01HGIQ9Qq677AtK5zqX63HgAe89WpPMMM5DM49dt6-qLKHPXZ2eIWUlsPnggQRtoA_mJx5mIZZO-CmItJrW-CkQpAeOOX0HOvm-F3UcKWoUzHIq3X6Kws_IdhjQPucSCGP-jHSvDDQkyIqUur9QldZ4Qiryi5QZqsR1MXRlEGS2pc.PW7ujZm2lhxcUy5w93K2zcxkZKY.ZrjRAg; canvas_session=R9cFJ0B8fw2kGghnM3hNVw+3mycko-nCqgy8W7XB2S1B-lsOjJEDPiMcF9gfUUwG_ZSYjTmHRwLDnGnZNNjH8sKeGO4MdElDodJnh6jrfuC6hwUdcducIJv-vZzk1vL-8q9pMKpW4D3sk-3T9BSgp8HtwPDyU1Z3KnVt8t7s86chnlGE7bnXI_uIVzKgU9sgo8hu0Gk9McrVo0i9pc4JzxLLqaj6fZ9oKDlc1YRQJ0ULQqLP4yMoHvF7bp-gohkCa4LAAlDY_bxwuou0anss_PQ7qugutoypqVGSSD006hFASi5ytVuzIwHNzjs_iTRE3jov8Ev-woaKH-7F2uzurpBtX2tPm2y3FYie4rY1fyM38kXVt7R5J1FAt7Px4reGoSfwMBuwjV96yKnha3SEkJhH0ctWKDdzpntWWoBqUa01HGIQ9Qq677AtK5zqX63HgAe89WpPMMM5DM49dt6-qLKHPXZ2eIWUlsPnggQRtoA_mJx5mIZZO-CmItJrW-CkQpAeOOX0HOvm-F3UcKWoUzHIq3X6Kws_IdhjQPucSCGP-jHSvDDQkyIqUur9QldZ4Qiryi5QZqsR1MXRlEGS2pc.PW7ujZm2lhxcUy5w93K2zcxkZKY.ZrjRAg; _csrf_token=ATOXpWqVntY79QQJid%2F6Y3TMlRNRfncHOBltyz6T1XRtHK%2FmGsXqoFKUMELtvNUKA6HXZwQRPzBeVjmOauLhMQ%3D%3D' \
  -H 'priority: u=1, i' \
  -H 'referer: https://tecsup.instructure.com/accounts/788/users?' \
  -H 'sec-ch-ua: "Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "macOS"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'sentry-trace: 2347c402bb804e2b8ea585c90eea1e26-9df8c5cb64c75566-0' \
  -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36' \
  -H 'x-csrf-token: ATOXpWqVntY79QQJid/6Y3TMlRNRfncHOBltyz6T1XRtHK/mGsXqoFKUMELtvNUKA6HXZwQRPzBeVjmOauLhMQ==' \
  -H 'x-requested-with: XMLHttpRequest'


curl 'https://tecsup.instructure.com/api/v1/accounts/788/courses?sort=teacher&order=asc&search_by=course&include%5B%5D=total_students&include%5B%5D=active_teachers&include%5B%5D=subaccount&include%5B%5D=term&include%5B%5D=concluded&include%5B%5D=ui_invoked&teacher_limit=25&per_page=15&no_avatar_fallback=1' \
  -H 'accept: application/json, text/javascript, application/json+canvas-string-ids, */*; q=0.01' \
  -H 'accept-language: en-US,en;q=0.9' \
  -H 'baggage: sentry-environment=Production,sentry-release=canvas-lms%4020240731.237,sentry-public_key=355a1d96717e4038ac25aa852fa79a8f,sentry-trace_id=be4c84215d904b12bbe7754e344f9fa3,sentry-sample_rate=0.005,sentry-sampled=false' \
  -H 'cookie: _mkto_trk=id:449-BVJ-543&token:_mch-instructure.com-1688505040122-89506; cb_user_id=null; cb_group_id=null; _ga=GA1.1.696460529.1688505041; __utmzz=utmcsr=google|utmcmd=organic|utmccn=(not set)|utmctr=(not provided); __utmzzses=1; _fbp=fb.1.1712240759262.1450090705; _gcl_au=1.1.292328603.1720465487; _clck=q67rpa%7C2%7Cfni%7C0%7C1413; _hp2_props.3295960117=%7B%22Region%22%3A%22Americas-North%20America%22%2C%22Page%20Node%22%3A%2224569%22%2C%22Page%20Group%22%3A%22Product%22%2C%22Page%20Type%22%3A%22Login%22%7D; _hp2_id.3295960117=%7B%22userId%22%3A%227093318029478131%22%2C%22pageviewId%22%3A%225688035975998059%22%2C%22sessionId%22%3A%227100528834732201%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D; _uetvid=e4f11c4082ee11eea73865cc4d7e1f12; _hp2_props.3001039959=%7B%22Base.appName%22%3A%22Canvas%22%7D; _hp2_id.3001039959=%7B%22userId%22%3A%226174738905007738%22%2C%22pageviewId%22%3A%225369478959062661%22%2C%22sessionId%22%3A%222908698223935315%22%2C%22identity%22%3A%22uu-2-0068b86a00b5fb00d5476a54fa940f2fc3a5e553e2bdff35e092d65d1c7d8f6a-ff2e5780-fa5b-012d-f7b3-123135003972%22%2C%22trackerVersion%22%3A%224.0%22%2C%22identityField%22%3Anull%2C%22isIdentified%22%3A1%7D; _ga_75H5134F9J=GS1.1.1721148870.41.0.1721148870.60.0.0; log_session_id=4ce20e7de0b5079e1568b0ea44c313ba; _legacy_normandy_session=xEIpz8L5jFnTGbXL0dJn2g+QY2cE7ghcqvoGS4hrHzw2g2bKa7MBFDlDEggbhAyAo3M4M_WIcfnxbyU2iQ4zwyWiH1QwaDQbPSpxziqxQu6OMtvQ_iRfXws6pY-DPWUEusjYoyzYdyc1-URdvBGiQ_3si12t2ZNcpTN6UyuWo5LRC9IYupkOTv9XUh5XH56upX7sC4Fu-fa9ZF7s42xVYXbFcAtn85bw73rbvMVCUGy2o-_xFc2MljUaJGTRwwJg7WdIa9EHMFSBAt8J7iCze4ER5tL-48VHJ60EopqSU2Orc_JP3AgVIwod2FJQaP1G4u757VN3m3u_KDkUmMJj77I0Ci3lzqQVivQtJp7mZcrN5q9t-gYCPbRITtcYfogUs_Df4Bz1zW1RA7ghVO_EffA3pgUIOFT7Em2TVVhSKF_Apht4KalbvU7krJ7i6iEvW1WS2zWoh1wl_0fAs3bDYXEhIeSznpbTtDzH8M9-hLOAyLcinMzML6ca-0utjWSqWAIPlcTs-mASigFAz-hl3qhaiJHa2VNdGGhrWv3FRmKFFgEz2JaHGbY_FJeweeoEGyKFJp0PivNwiL8yLvNAtCJ.NCfyG2euHxXwTjCZu6m5fNP9NEQ.ZroxRA; canvas_session=xEIpz8L5jFnTGbXL0dJn2g+QY2cE7ghcqvoGS4hrHzw2g2bKa7MBFDlDEggbhAyAo3M4M_WIcfnxbyU2iQ4zwyWiH1QwaDQbPSpxziqxQu6OMtvQ_iRfXws6pY-DPWUEusjYoyzYdyc1-URdvBGiQ_3si12t2ZNcpTN6UyuWo5LRC9IYupkOTv9XUh5XH56upX7sC4Fu-fa9ZF7s42xVYXbFcAtn85bw73rbvMVCUGy2o-_xFc2MljUaJGTRwwJg7WdIa9EHMFSBAt8J7iCze4ER5tL-48VHJ60EopqSU2Orc_JP3AgVIwod2FJQaP1G4u757VN3m3u_KDkUmMJj77I0Ci3lzqQVivQtJp7mZcrN5q9t-gYCPbRITtcYfogUs_Df4Bz1zW1RA7ghVO_EffA3pgUIOFT7Em2TVVhSKF_Apht4KalbvU7krJ7i6iEvW1WS2zWoh1wl_0fAs3bDYXEhIeSznpbTtDzH8M9-hLOAyLcinMzML6ca-0utjWSqWAIPlcTs-mASigFAz-hl3qhaiJHa2VNdGGhrWv3FRmKFFgEz2JaHGbY_FJeweeoEGyKFJp0PivNwiL8yLvNAtCJ.NCfyG2euHxXwTjCZu6m5fNP9NEQ.ZroxRA; _csrf_token=8fNmPE1tQYcp3vhVF0VdmrPBNSioG1lDvXyYIUekLEOBtTV4DBUD9gKGyC1Ydi7O1bVRS8MqFyGJPt9mc%2BFFJA%3D%3D' \
  -H 'priority: u=1, i' \
  -H 'referer: https://tecsup.instructure.com/accounts/788?sort=teacher' \
  -H 'sec-ch-ua: "Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "macOS"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'sentry-trace: be4c84215d904b12bbe7754e344f9fa3-9fd8511e2dc05ac5-0' \
  -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36' \
  -H 'x-csrf-token: 8fNmPE1tQYcp3vhVF0VdmrPBNSioG1lDvXyYIUekLEOBtTV4DBUD9gKGyC1Ydi7O1bVRS8MqFyGJPt9mc+FFJA==' \
  -H 'x-requested-with: XMLHttpRequest'
  
'''