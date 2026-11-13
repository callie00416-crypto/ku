import request from '/@/utils/request';

// 测试用例管理
export function getTestCaseList(data: any) {
  return request({
    url: '/api/encoder_test/test-cases/',
    method: 'get',
    params: data
  });
}

export function addTestCase(data: any) {
  return request({
    url: '/api/encoder_test/test-cases/',
    method: 'post',
    data
  });
}

export function updateTestCase(data: any) {
  return request({
    url: `/api/encoder_test/test-cases/${data.id}/`,
    method: 'put',
    data
  });
}

export function deleteTestCase(id: number) {
  return request({
    url: `/api/encoder_test/test-cases/${id}/`,
    method: 'delete'
  });
}

export function executeTestCase(id: number) {
  return request({
    url: `/api/encoder_test/test-cases/${id}/execute/`,
    method: 'post'
  });
}

export function batchUpdateTestCaseStatus(ids: number[], status: string) {
  return request({
    url: '/api/encoder_test/test-cases/batch-update-status/',
    method: 'post',
    data: { ids, status }
  });
}

// 测试任务管理
export function getTestTaskList(data: any) {
  return request({
    url: '/api/encoder_test/test-tasks/',
    method: 'get',
    params: data
  });
}

export function addTestTask(data: any) {
  return request({
    url: '/api/encoder_test/test-tasks/',
    method: 'post',
    data
  });
}

export function updateTestTask(data: any) {
  return request({
    url: `/api/encoder_test/test-tasks/${data.id}/`,
    method: 'put',
    data
  });
}

export function deleteTestTask(id: number) {
  return request({
    url: `/api/encoder_test/test-tasks/${id}/`,
    method: 'delete'
  });
}

export function startTestTask(id: number) {
  return request({
    url: `/api/encoder_test/test-tasks/${id}/start/`,
    method: 'post'
  });
}

export function stopTestTask(id: number) {
  return request({
    url: `/api/encoder_test/test-tasks/${id}/stop/`,
    method: 'post'
  });
}

// 测试报告管理
export function getTestReportList(data: any) {
  return request({
    url: '/api/encoder_test/test-reports/',
    method: 'get',
    params: data
  });
}

export function getTestReportDetail(id: number) {
  return request({
    url: `/api/encoder_test/test-reports/${id}/`,
    method: 'get'
  });
}

export function deleteTestReport(id: number) {
  return request({
    url: `/api/encoder_test/test-reports/${id}/`,
    method: 'delete'
  });
}

// 扫描器管理
export function scanTestCases() {
  return request({
    url: '/api/encoder_test/scanner/scan/',
    method: 'post'
  });
}

export function previewTestCases() {
  return request({
    url: '/api/encoder_test/scanner/preview/',
    method: 'get'
  });
}

// 工位管理
export * from './station';
