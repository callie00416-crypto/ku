<template>
  <div class="station-monitor-container">
    <el-card class="header-card">
      <div class="header-content">
        <h2>工位监控</h2>
        <div class="header-info">
          <span class="time">{{ currentTime }}</span>
          <el-button type="primary" @click="refreshStations">
            <el-icon><Refresh /></el-icon> 刷新
          </el-button>
        </div>
      </div>
    </el-card>

    <div class="stations-grid">
      <el-card
        v-for="station in stations"
        :key="station.id"
        class="station-card"
        :class="{ 'running': station.status === 'running' }"
      >
        <div class="station-header">
          <div class="station-status">
            <div class="status-dot" :class="station.status"></div>
            <h3>{{ station.name }}</h3>
          </div>
          <el-tag :type="station.status === 'running' || station.status === 'completed' ? 'success' : station.status === 'paused' ? 'warning' : station.status === 'failed' || station.status === 'error' ? 'danger' : 'info'" size="large">
            {{ station.status === 'running' ? '运行中' : station.status === 'completed' ? '已完成' : station.status === 'paused' ? '已暂停' : station.status === 'failed' ? '失败' : station.status === 'error' ? '错误' : '空闲' }}
          </el-tag>
        </div>

        <el-divider />

        <div class="station-info">
          <div class="info-item">
            <label>工位编号:</label>
            <span>ST{{ String(station.id).padStart(3, '0') }}</span>
          </div>
          <div class="info-item">
            <label>当前产品:</label>
            <span>{{ station.product_sn || '无' }}</span>
          </div>
          <div class="info-item">
            <label>测试进度:</label>
            <el-progress
              :percentage="station.progress"
              :status="station.status === 'running' ? undefined : 'success'"
            />
          </div>
        </div>

        <div class="station-actions">
          <el-button
            v-if="!station.status || station.status === 'idle' || station.status === 'completed'"
            type="primary"
            @click="openTestDialog(station)"
            block
          >
            开始测试
          </el-button>
          <div v-else-if="station.status" class="control-buttons">
            <el-button
              v-if="station.status === 'running'"
              type="warning"
              @click="pauseTest(station)"
              :icon="VideoPause"
            >
              暂停
            </el-button>
            <el-button
              v-if="station.status === 'paused'"
              type="success"
              @click="resumeTest(station)"
              :icon="VideoPlay"
            >
              恢复
            </el-button>
            <el-button
              v-if="station.status === 'running' || station.status === 'paused'"
              type="danger"
              @click="stopTest(station)"
              :icon="VideoCamera"
            >
              停止
            </el-button>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 系统日志和实时数据曲线 -->
    <div class="bottom-section">
      <el-card class="log-card">
        <template #header>
          <div class="card-header">
            <span>系统日志</span>
            <el-select v-model="logLevel" size="small" style="width: 120px">
              <el-option label="全部" value="all" />
              <el-option label="信息" value="info" />
              <el-option label="警告" value="warning" />
              <el-option label="错误" value="error" />
            </el-select>
          </div>
        </template>
        <div class="log-content">
          <div v-for="(log, index) in filteredLogs" :key="index" class="log-item">
            <span class="log-time">{{ log.time }}</span>
            <el-tag :type="log.level === 'error' ? 'danger' : log.level === 'warning' ? 'warning' : 'info'" size="small">
              {{ log.level.toUpperCase() }}
            </el-tag>
            <span class="log-message">{{ log.message }}</span>
          </div>
        </div>
      </el-card>

      <el-card class="chart-card">
        <template #header>
          <span>实时数据曲线</span>
        </template>
        <div ref="chartRef" class="chart-container"></div>
      </el-card>
    </div>

    <!-- 测试配置对话框 -->
    <el-dialog
      v-model="testDialogVisible"
      :title="`工位 ${currentStation?.id} - 测试配置`"
      width="600px"
    >
      <el-form :model="testForm" label-width="100px">
        <el-form-item label="产品SN">
          <el-input v-model="testForm.productSn" placeholder="扫描或输入产品SN码" />
        </el-form-item>
        <el-form-item label="产品型号">
          <el-select v-model="testForm.productModel" placeholder="请选择产品型号">
            <el-option label="型号A" value="A" />
            <el-option label="型号B" value="B" />
            <el-option label="型号C" value="C" />
          </el-select>
        </el-form-item>
        <el-form-item label="测试用例">
          <el-table :data="availableCases" @selection-change="handleCaseSelection" max-height="300">
            <el-table-column type="selection" width="55" />
            <el-table-column prop="name" label="用例编号" />
            <el-table-column prop="description" label="用例名称" show-overflow-tooltip />
          </el-table>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="testDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="startTest" :loading="starting">开始测试</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts" name="stationMonitor">
import { ref, reactive, onMounted, onUnmounted, computed } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Refresh, VideoPause, VideoPlay, VideoCamera } from '@element-plus/icons-vue';
import {
  getStationList,
  startStationTest,
  pauseStationTest,
  resumeStationTest,
  stopStationTest
} from '/@/api/encoder_test/station';
import { getTestCaseList } from '/@/api/encoder_test';
import * as echarts from 'echarts';

const currentTime = ref('');
const stations = ref<any[]>([]);
const logLevel = ref('all');
const logs = ref<any[]>([]);
const testDialogVisible = ref(false);
const currentStation = ref<any>(null);
const starting = ref(false);
const chartRef = ref<HTMLElement>();
let chart: any = null;
let timer: any = null;

const testForm = reactive({
  productSn: '',
  productModel: '',
  selectedCases: []
});

const availableCases = ref<any[]>([]);

const filteredLogs = computed(() => {
  if (logLevel.value === 'all') return logs.value;
  return logs.value.filter(log => log.level === logLevel.value);
});

// 获取状态类型
const getStatusType = (status: string) => {
  const typeMap: any = {
    'idle': 'info',
    'running': 'success',
    'paused': 'warning',
    'completed': 'success',
    'failed': 'danger',
    'error': 'danger'
  };
  return typeMap[status] || 'info';
};

// 获取状态文本
const getStatusText = (status: string) => {
  const textMap: any = {
    'idle': '空闲',
    'running': '运行中',
    'paused': '已暂停',
    'completed': '已完成',
    'failed': '失败',
    'error': '错误'
  };
  return textMap[status] || '未知';
};

// 更新时间
const updateTime = () => {
  const now = new Date();
  currentTime.value = now.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
};

// 刷新工位状态
const refreshStations = async () => {
  try {
    const res = await getStationList();
    if (res.code === 2000) {
      stations.value = res.data;
      
      // 只在有运行中的任务时添加日志
      const hasRunningTask = res.data.some((s: any) => s.status === 'running');
      if (hasRunningTask) {
        addLog('info', '工位状态已刷新');
      }
      
      // 检查是否有运行中的任务，如果有且定时器未启动，则重新启动
      if (hasRunningTask && !timer) {
        console.log('检测到运行中的任务，启动自动刷新');
        startAutoRefresh();
      }
    }
  } catch (error) {
    ElMessage.error('刷新工位状态失败');
  }
};

// 打开测试对话框
const openTestDialog = async (station: any) => {
  currentStation.value = station;
  testForm.productSn = '';
  testForm.productModel = '';
  testForm.selectedCases = [];
  testDialogVisible.value = true;

  // 加载可用用例
  try {
    const res = await getTestCaseList({ limit: 100 });
    if (res.code === 2000) {
      availableCases.value = res.data.filter((item: any) => item.status === 'active');
    }
  } catch (error) {
    console.error(error);
  }
};

// 用例选择
const handleCaseSelection = (selection: any[]) => {
  testForm.selectedCases = selection;
};

// 开始测试
const startTest = async () => {
  if (!testForm.productSn) {
    ElMessage.warning('请输入产品SN码');
    return;
  }
  if (testForm.selectedCases.length === 0) {
    ElMessage.warning('请选择测试用例');
    return;
  }

  starting.value = true;
  try {
    const res = await startStationTest({
      station_id: currentStation.value.id,
      product_sn: testForm.productSn,
      case_ids: testForm.selectedCases.map((c: any) => c.id)
    });

    if (res.code === 2000) {
      ElMessage.success(res.msg);
      testDialogVisible.value = false;
      addLog('info', `工位${currentStation.value.id}开始测试: ${testForm.productSn}`);
      refreshStations();
    } else {
      ElMessage.error(res.msg);
    }
  } catch (error: any) {
    ElMessage.error('启动测试失败: ' + (error.response?.data?.msg || error.message));
  } finally {
    starting.value = false;
  }
};

// 暂停测试
const pauseTest = async (station: any) => {
  try {
    await ElMessageBox.confirm(`确定要暂停工位${station.id}的测试吗？`, '提示', {
      type: 'warning'
    });

    const res = await pauseStationTest({ station_id: station.id });
    if (res.code === 2000) {
      ElMessage.success(res.msg);
      addLog('warning', `工位${station.id}测试已暂停`);
      refreshStations();
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('暂停测试失败');
    }
  }
};

// 恢复测试
const resumeTest = async (station: any) => {
  try {
    const res = await resumeStationTest({ station_id: station.id });
    if (res.code === 2000) {
      ElMessage.success(res.msg);
      addLog('info', `工位${station.id}测试已恢复`);
      refreshStations();
    }
  } catch (error) {
    ElMessage.error('恢复测试失败');
  }
};

// 停止测试
const stopTest = async (station: any) => {
  try {
    await ElMessageBox.confirm(`确定要停止工位${station.id}的测试吗？`, '提示', {
      type: 'warning'
    });

    const res = await stopStationTest({ station_id: station.id });
    if (res.code === 2000) {
      ElMessage.success(res.msg);
      addLog('error', `工位${station.id}测试已停止`);
      refreshStations();
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('停止测试失败');
    }
  }
};

// 添加日志
const addLog = (level: string, message: string) => {
  const now = new Date();
  const time = now.toLocaleTimeString('zh-CN');
  logs.value.unshift({ time, level, message });
  if (logs.value.length > 100) {
    logs.value.pop();
  }
};

// 初始化图表
const initChart = () => {
  if (!chartRef.value) return;
  
  chart = echarts.init(chartRef.value);
  const option = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['工位-1号', '工位-2号', '工位-3号'] },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: []
    },
    yAxis: {
      type: 'value',
      name: '进度(%)',
      max: 100
    },
    series: [
      { name: '工位-1号', type: 'line', data: [] },
      { name: '工位-2号', type: 'line', data: [] },
      { name: '工位-3号', type: 'line', data: [] }
    ]
  };
  chart.setOption(option);
};

// 更新图表数据
const updateChart = () => {
  if (!chart) return;
  
  const now = new Date().toLocaleTimeString('zh-CN');
  const option = {
    xAxis: {
      data: [...chart.getOption().xAxis[0].data, now].slice(-10)
    },
    series: stations.value.map((station, index) => ({
      data: [...(chart.getOption().series[index]?.data || []), station.progress].slice(-10)
    }))
  };
  chart.setOption(option);
};

// 定时刷新
const startAutoRefresh = () => {
  timer = setInterval(() => {
    // 检查是否有工位正在运行
    const hasRunningTask = stations.value.some(s => s.status === 'running' || s.status === 'paused');
    
    if (hasRunningTask) {
      // 有运行中的任务，继续刷新
      refreshStations();
      updateChart();
    } else {
      // 没有运行中的任务，停止刷新（节省资源）
      console.log('所有工位空闲，停止自动刷新');
      clearInterval(timer);
      timer = null;
    }
  }, 2000);
};

onMounted(() => {
  updateTime();
  refreshStations();
  initChart();
  startAutoRefresh();
  
  // 每秒更新时间
  setInterval(updateTime, 1000);
});

onUnmounted(() => {
  if (timer) clearInterval(timer);
  if (chart) chart.dispose();
});
</script>

<style scoped>
.station-monitor-container {
  padding: 20px;
}

.header-card {
  margin-bottom: 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-content h2 {
  margin: 0;
}

.header-info {
  display: flex;
  align-items: center;
  gap: 20px;
}

.time {
  font-size: 18px;
  color: #606266;
}

.stations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.station-card {
  transition: all 0.3s;
}

.station-card.running {
  border-color: #67c23a;
  box-shadow: 0 2px 12px 0 rgba(103, 194, 58, 0.3);
}

.station-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.station-status {
  display: flex;
  align-items: center;
  gap: 10px;
}

.status-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #909399;
}

.status-dot.running {
  background: #67c23a;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.station-info {
  margin: 15px 0;
}

.info-item {
  margin-bottom: 10px;
  display: flex;
  align-items: center;
}

.info-item label {
  font-weight: bold;
  margin-right: 10px;
  min-width: 80px;
}

.station-actions {
  margin-top: 15px;
}

.control-buttons {
  display: flex;
  gap: 10px;
}

.control-buttons .el-button {
  flex: 1;
}

.bottom-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.log-content {
  max-height: 400px;
  overflow-y: auto;
}

.log-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px;
  border-bottom: 1px solid #ebeef5;
}

.log-time {
  color: #909399;
  font-size: 12px;
  min-width: 80px;
}

.log-message {
  flex: 1;
}

.chart-container {
  height: 400px;
}

@media (max-width: 768px) {
  .bottom-section {
    grid-template-columns: 1fr;
  }
}
</style>
