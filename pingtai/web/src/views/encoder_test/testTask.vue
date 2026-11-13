<template>
  <div class="app-container">
    <el-card>
      <div class="table-toolbar">
        <el-button type="primary" @click="handleAdd">新增任务</el-button>
      </div>

      <el-table :data="tableData" v-loading="loading" border>
        <el-table-column prop="name" label="任务名称" min-width="150" />
        <el-table-column prop="test_case_name" label="测试用例" min-width="150" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.status === 'pending'" type="info">待执行</el-tag>
            <el-tag v-else-if="row.status === 'running'" type="warning">执行中</el-tag>
            <el-tag v-else-if="row.status === 'passed'" type="success">通过</el-tag>
            <el-tag v-else-if="row.status === 'failed'" type="danger">失败</el-tag>
            <el-tag v-else-if="row.status === 'error'" type="danger">错误</el-tag>
            <el-tag v-else-if="row.status === 'stopped'" type="info">已停止</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="started_at" label="开始时间" width="180" />
        <el-table-column prop="completed_at" label="完成时间" width="180" />
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'pending'"
              type="success"
              size="small"
              @click="handleStart(row)"
            >
              启动
            </el-button>
            <el-button
              v-if="row.status === 'running'"
              type="warning"
              size="small"
              @click="handleStop(row)"
            >
              停止
            </el-button>
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

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      @close="handleDialogClose"
    >
      <el-form :model="formData" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="任务名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入任务名称" />
        </el-form-item>
        <el-form-item label="测试用例" prop="test_case">
          <el-select v-model="formData.test_case" placeholder="请选择测试用例">
            <el-option
              v-for="item in testCaseList"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts" name="encoderTestTask">
import { ref, reactive, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import {
  getTestTaskList,
  addTestTask,
  updateTestTask,
  deleteTestTask,
  startTestTask,
  stopTestTask
} from '/@/api/encoder_test';
import { getTestCaseList } from '/@/api/encoder_test';

const loading = ref(false);
const tableData = ref([]);
const testCaseList = ref([]);
const dialogVisible = ref(false);
const dialogTitle = ref('');
const formRef = ref();

const pagination = reactive({
  page: 1,
  limit: 10,
  total: 0
});

const formData = reactive({
  id: undefined,
  name: '',
  test_case: undefined
});

const rules = {
  name: [{ required: true, message: '请输入任务名称', trigger: 'blur' }],
  test_case: [{ required: true, message: '请选择测试用例', trigger: 'change' }]
};

// 获取任务列表
const getList = async () => {
  loading.value = true;
  try {
    const params = {
      page: pagination.page,
      limit: pagination.limit
    };
    const res = await getTestTaskList(params);
    tableData.value = res.data;
    pagination.total = res.total;
  } catch (error) {
    console.error(error);
  } finally {
    loading.value = false;
  }
};

// 获取用例列表
const getTestCaseListData = async () => {
  try {
    const res = await getTestCaseList({ limit: 100 });
    testCaseList.value = res.data;
  } catch (error) {
    console.error(error);
  }
};

// 新增
const handleAdd = () => {
  dialogTitle.value = '新增测试任务';
  dialogVisible.value = true;
};

// 编辑
const handleEdit = (row: any) => {
  dialogTitle.value = '编辑测试任务';
  Object.assign(formData, row);
  dialogVisible.value = true;
};

// 删除
const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定要删除该任务吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    });
    await deleteTestTask(row.id);
    ElMessage.success('删除成功');
    getList();
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error);
    }
  }
};

// 启动
const handleStart = async (row: any) => {
  try {
    await ElMessageBox.confirm(`确定要启动任务 "${row.name}" 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    });
    const res = await startTestTask(row.id);
    ElMessage.success(res.message || '启动成功');
    getList();
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error);
    }
  }
};

// 停止
const handleStop = async (row: any) => {
  try {
    await ElMessageBox.confirm(`确定要停止任务 "${row.name}" 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    });
    const res = await stopTestTask(row.id);
    ElMessage.success(res.message || '停止成功');
    getList();
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error);
    }
  }
};

// 提交
const handleSubmit = async () => {
  try {
    await formRef.value.validate();
    
    if (formData.id) {
      await updateTestTask(formData);
      ElMessage.success('更新成功');
    } else {
      await addTestTask(formData);
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
    test_case: undefined
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
  getTestCaseListData();
});
</script>

<style scoped>
.table-toolbar {
  margin-bottom: 20px;
}
</style>
