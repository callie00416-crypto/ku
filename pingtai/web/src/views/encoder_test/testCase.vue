<template>
  <div class="app-container">
    <el-card>
      <div class="table-search">
        <el-form :model="searchForm" inline>
          <el-form-item label="用例名称">
            <el-input v-model="searchForm.name" placeholder="请输入用例名称" clearable />
          </el-form-item>
          <el-form-item label="测试类型">
            <el-select v-model="searchForm.test_type" placeholder="请选择测试类型" clearable>
              <el-option label="单元测试" value="unit" />
              <el-option label="集成测试" value="integration" />
              <el-option label="电源测试" value="power_supply" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">查询</el-button>
            <el-button @click="handleReset">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <div class="table-toolbar">
        <el-button type="success" @click="handleScan">扫描用例</el-button>
        <el-button type="primary" @click="handleAdd">新增用例</el-button>
        <el-button type="warning" @click="handleBatchDisable" :disabled="!multipleSelection.length">
          批量禁用
        </el-button>
        <el-button type="info" @click="handleBatchEnable" :disabled="!multipleSelection.length">
          批量启用
        </el-button>
        <span v-if="multipleSelection.length" style="margin-left: 10px; color: #606266">
          已选择 <strong>{{ multipleSelection.length }}</strong> 项
        </span>
        <el-switch
          v-model="executeInNewTab"
          class="execute-mode-switch"
          style="margin-left: 20px"
          active-text="任务页面模式"
          inactive-text="弹窗模式"
        />
      </div>

      <el-table :data="tableData" v-loading="loading" border @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="55" />
        <el-table-column prop="name" label="用例名称" min-width="150" />
        <el-table-column prop="test_type" label="测试类型" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.test_type === 'unit'">单元测试</el-tag>
            <el-tag v-else-if="row.test_type === 'integration'" type="success">集成测试</el-tag>
            <el-tag v-else-if="row.test_type === 'power_supply'" type="warning">电源测试</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">
              {{ row.status === 'active' ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleExecute(row)">执行</el-button>
            <el-button type="primary" size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.limit"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </el-card>

    <!-- 执行详情弹窗 -->
    <el-dialog
      v-model="executeDialogVisible"
      title="执行详情"
      width="700px"
      :close-on-click-modal="false"
    >
      <div v-if="executeResult" class="execute-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="用例名称">{{ currentCase?.name }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="executeResult.status === 'running' ? 'warning' : 'success'">
              {{ executeResult.status === 'running' ? '执行中' : '执行完成' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="执行信息" :span="2">
            <div class="execute-message">{{ executeResult.message }}</div>
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="executeDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      @close="handleDialogClose"
    >
      <el-form :model="formData" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="用例名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入用例名称" />
        </el-form-item>
        <el-form-item label="测试类型" prop="test_type">
          <el-select v-model="formData.test_type" placeholder="请选择测试类型">
            <el-option label="单元测试" value="unit" />
            <el-option label="集成测试" value="integration" />
            <el-option label="电源测试" value="power_supply" />
          </el-select>
        </el-form-item>
        <el-form-item label="脚本路径" prop="script_path">
          <el-input v-model="formData.script_path" placeholder="请输入脚本路径" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="formData.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="测试参数">
          <el-input v-model="formData.parameters_json" type="textarea" :rows="3" placeholder='{"key": "value"}' />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="formData.status" active-value="active" inactive-value="inactive" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts" name="encoderTestCase">
import { ref, reactive, onMounted, watch } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import {
  getTestCaseList,
  addTestCase,
  updateTestCase,
  deleteTestCase,
  executeTestCase,
  scanTestCases,
  batchUpdateTestCaseStatus
} from '/@/api/encoder_test';
import { Local } from '/@/utils/storage';

const loading = ref(false);
const tableData = ref([]);
const multipleSelection = ref([]);
const dialogVisible = ref(false);
const dialogTitle = ref('');
const formRef = ref();

// 执行模式配置
const executeInNewTab = ref(Local.get('executeInNewTab') || false); // false: 弹窗模式, true: 任务页面模式

// 监听执行模式变化，保存到本地存储
watch(executeInNewTab, (newVal) => {
  Local.set('executeInNewTab', newVal);
});

// 执行相关
const executeDialogVisible = ref(false);
const executeResult = ref<any>(null);
const currentCase = ref<any>(null);

const searchForm = reactive({
  name: '',
  test_type: ''
});

const pagination = reactive({
  page: 1,
  limit: 10,
  total: 0
});

const formData = reactive({
  id: undefined,
  name: '',
  test_type: '',
  script_path: '',
  description: '',
  parameters_json: '{}',
  status: 'active'
});

const rules = {
  name: [{ required: true, message: '请输入用例名称', trigger: 'blur' }],
  test_type: [{ required: true, message: '请选择测试类型', trigger: 'change' }],
  script_path: [{ required: true, message: '请输入脚本路径', trigger: 'blur' }]
};

// 获取列表
const getList = async () => {
  loading.value = true;
  try {
    const params = {
      page: pagination.page,
      limit: pagination.limit,
      ...searchForm
    };
    const res = await getTestCaseList(params);
    console.log('列表响应:', res);
    // dvadmin 框架返回格式: {code: 2000, data: [...], total: 2, msg: "..."}
    tableData.value = res.data || [];
    pagination.total = res.total || 0;
    console.log('表格数据:', tableData.value, '总数:', pagination.total);
  } catch (error: any) {
    console.error('获取列表失败:', error);
    ElMessage.error('获取列表失败: ' + (error.response?.data?.msg || error.message));
  } finally {
    loading.value = false;
  }
};

// 搜索
const handleSearch = () => {
  pagination.page = 1;
  getList();
};

// 扫描用例
const handleScan = async () => {
  try {
    const res = await scanTestCases();
    console.log('扫描结果:', res);
    if (res.code === 2000) {
      ElMessage.success(res.msg);
      getList(); // 扫描成功后自动刷新列表
    } else {
      ElMessage.error(res.msg || '扫描失败');
    }
  } catch (error: any) {
    console.error('扫描错误:', error);
    const errorMsg = error.response?.data?.msg || error.message || '扫描失败，请检查后端服务';
    ElMessage.error(errorMsg);
  }
};

// 多选处理
const handleSelectionChange = (val: any[]) => {
  multipleSelection.value = val;
};

// 批量禁用
const handleBatchDisable = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要禁用选中的 ${multipleSelection.value.length} 个用例吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    );
    
    const ids = multipleSelection.value.map(item => item.id);
    await batchUpdateTestCaseStatus(ids, 'inactive');
    ElMessage.success('批量禁用成功');
    multipleSelection.value = [];
    getList();
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error);
      ElMessage.error('批量禁用失败');
    }
  }
};

// 批量启用
const handleBatchEnable = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要启用选中的 ${multipleSelection.value.length} 个用例吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info'
      }
    );
    
    const ids = multipleSelection.value.map(item => item.id);
    await batchUpdateTestCaseStatus(ids, 'active');
    ElMessage.success('批量启用成功');
    multipleSelection.value = [];
    getList();
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error);
      ElMessage.error('批量启用失败');
    }
  }
};

// 重置
const handleReset = () => {
  searchForm.name = '';
  searchForm.test_type = '';
  handleSearch();
};

// 新增
const handleAdd = () => {
  dialogTitle.value = '新增测试用例';
  dialogVisible.value = true;
};

// 编辑
const handleEdit = (row: any) => {
  dialogTitle.value = '编辑测试用例';
  Object.assign(formData, row);
  formData.parameters_json = JSON.stringify(row.parameters || {});
  dialogVisible.value = true;
};

// 删除
const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定要删除该用例吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    });
    await deleteTestCase(row.id);
    ElMessage.success('删除成功');
    getList();
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error);
    }
  }
};

// 执行
const handleExecute = async (row: any) => {
  try {
    await ElMessageBox.confirm(`确定要执行用例 "${row.name}" 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    });
    
    // 根据配置选择执行模式
    if (executeInNewTab.value) {
      // 任务页面模式：创建任务并跳转
      await executeInTaskMode(row);
    } else {
      // 弹窗模式：当前页面显示执行详情
      await executeInDialogMode(row);
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error);
    }
  }
};

// 弹窗模式执行
const executeInDialogMode = async (row: any) => {
  // 设置当前用例和初始状态
  currentCase.value = row;
  executeResult.value = {
    status: 'running',
    message: '开始执行测试用例...'
  };
  executeDialogVisible.value = true;
  
  try {
    // 调用执行 API
    const res = await executeTestCase(row.id);
    
    // 更新执行结果
    executeResult.value = {
      status: res.status || 'completed',
      message: res.message || '执行完成'
    };
  } catch (error) {
    ElMessage.error('执行失败');
    executeResult.value = {
      status: 'error',
      message: error.response?.data?.msg || error.message || '执行失败'
    };
  }
};

// 任务页面模式执行
const executeInTaskMode = async (row: any) => {
  try {
    // 创建测试任务
    const taskData = {
      name: `${row.name} - ${new Date().toLocaleString()}`,
      test_case: row.id
    };
    
    // 调用创建任务 API
    const { addTestTask } = await import('/@/api/encoder_test');
    const taskRes = await addTestTask(taskData);
    
    console.log('任务创建响应:', taskRes);
    
    // 获取任务ID
    const taskId = taskRes.data?.id || taskRes.id;
    if (!taskId) {
      throw new Error('未获取到任务ID');
    }
    
    // 启动任务
    const { startTestTask } = await import('/@/api/encoder_test');
    await startTestTask(taskId);
    
    ElMessage.success('任务已创建并启动');
    
    // 跳转到任务管理页面
    window.open('/#/encoder-test/test-task', '_blank');
  } catch (error: any) {
    console.error('任务创建失败:', error);
    ElMessage.error('创建任务失败: ' + (error.response?.data?.msg || error.message));
    throw error;
  }
};

// 提交
const handleSubmit = async () => {
  try {
    await formRef.value.validate();
    const data = {
      ...formData,
      parameters: JSON.parse(formData.parameters_json || '{}')
    };
    
    if (formData.id) {
      await updateTestCase(data);
      ElMessage.success('更新成功');
    } else {
      await addTestCase(data);
      ElMessage.success('新增成功');
    }
    
    dialogVisible.value = false;
    getList();
  } catch (error) {
    console.error(error);
  }
};

// 对话框关闭
const handleDialogClose = () => {
  formRef.value?.resetFields();
  Object.assign(formData, {
    id: undefined,
    name: '',
    test_type: '',
    script_path: '',
    description: '',
    parameters_json: '{}',
    status: 'active'
  });
};

// 分页
const handleSizeChange = () => {
  getList();
};

const handlePageChange = () => {
  getList();
};

onMounted(() => {
  getList();
});
</script>

<style scoped>
.table-search {
  margin-bottom: 20px;
}

.table-toolbar {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
}

.execute-mode-switch {
  margin-left: auto;
}

.execute-detail {
  padding: 20px 0;
}

.execute-message {
  line-height: 1.6;
  color: #606266;
  font-size: 14px;
}
</style>
