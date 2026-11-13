import request from '/@/utils/request';

// 工位管理
export function getStationList() {
  return request({
    url: '/api/encoder_test/stations/list/',
    method: 'get'
  });
}

export function startStationTest(data: any) {
  return request({
    url: '/api/encoder_test/stations/start-test/',
    method: 'post',
    data
  });
}

export function pauseStationTest(data: any) {
  return request({
    url: '/api/encoder_test/stations/pause-test/',
    method: 'post',
    data
  });
}

export function resumeStationTest(data: any) {
  return request({
    url: '/api/encoder_test/stations/resume-test/',
    method: 'post',
    data
  });
}

export function stopStationTest(data: any) {
  return request({
    url: '/api/encoder_test/stations/stop-test/',
    method: 'post',
    data
  });
}

export function getTaskDetail(taskId: string) {
  return request({
    url: '/api/encoder_test/stations/task-detail/',
    method: 'get',
    params: { task_id: taskId }
  });
}
