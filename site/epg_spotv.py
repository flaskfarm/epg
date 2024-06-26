from support import d, default_headers

from ..setup import *


class EpgSpotv(object):
    @classmethod
    def make_epg(cls):
        try:
            
                epg_data = {}
                current_dt = datetime.now()
                for i in range(6):
                    param_dt = current_dt + timedelta(days=i)
                    param = param_dt.strftime('%Y-%m-%d')
                    url = f"https://www.spotvnow.co.kr/api/v3/program/{param}"
                    logger.debug(f"SPOTV EPG URL : {url}")
                    try:
                        data = requests.get(url, headers=default_headers).json()
                        logger.debug(f"{param} : {len(data)}")
                        for item in data:
                            if item['channelId'] not in epg_data:
                                epg_data[item['channelId']] = []
                            epg_data[item['channelId']].append(item)
                    except:
                        break
                
                for ch_id, ch_data in epg_data.items():
                    db_item = ModelEpgChannel.get_by_source_id('spotv', ch_id) 
                    if db_item == None:
                        logger.error(f"확인필요 채널 ID : {ch_id}")
                        continue
                    ModelEpgProgram.delete_by_channel_name(db_item.name)
                    count = 0
                    for item in ch_data:
                        p = ModelEpgProgram()
                        p.channel = db_item
                        p.start_time = datetime.strptime(item['startTime'], '%Y-%m-%d %H:%M')
                        if item['endTime'] == '':
                            p.end_time = datetime(p.start_time.year, p.start_time.month, p.start_time.day, 23, 59, 59)
                        else:
                            p.end_time = datetime.strptime(item['endTime'], '%Y-%m-%d %H:%M')
                        p.title = item['title']
                        db.session.add(p)
                        count += 1
                    db_item.update_time = current_dt
                    db_item.epg_from = 'spotv'
                    #db_item.save()
                    db.session.add(db_item)
                    logger.warning(f"{db_item.name} {count}개 추가")
                db.session.commit()
                return True
        except Exception as e: 
            logger.error(f'Exception:{str(e)}')
            logger.error(traceback.format_exc())
            return False

