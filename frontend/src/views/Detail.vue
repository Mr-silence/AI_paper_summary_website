<template>
  <div class="detail-page">
    <div class="page-header">
      <el-button :icon="Back" @click="$router.back()">返回</el-button>
    </div>

    <div v-if="loading" class="loading-state">
      <el-skeleton :rows="10" animated />
    </div>

    <div v-else-if="paper" class="paper-article">
      <h1 class="article-title">{{ paper.title }}</h1>
      <div class="article-meta">
        <el-tag size="small" type="info">{{ paper.issue_date }}</el-tag>
        <span class="authors">作者: {{ paper.authors.join(', ') }}</span>
      </div>

      <div class="ai-summary-section">
        <el-alert
          title="💡 一句话总结"
          :description="paper.one_line_summary"
          type="success"
          :closable="false"
          class="highlight-alert"
        />

        <div class="section-block">
          <h3>✨ 核心亮点</h3>
          <ul>
            <li v-for="(item, index) in paper.core_highlights" :key="index">
              {{ item }}
            </li>
          </ul>
        </div>

        <div class="section-block">
          <h3>🚀 应用场景</h3>
          <p>{{ paper.application_scenarios }}</p>
        </div>
      </div>

      <div class="original-section">
        <el-collapse>
          <el-collapse-item title="查看原论文英文摘要 (Abstract)" name="1">
            <p class="abstract-text">{{ paper.abstract }}</p>
            <div class="pdf-link">
              <el-button type="primary" plain tag="a" :href="paper.pdf_url" target="_blank" :icon="Document">
                下载 PDF 原文
              </el-button>
              <el-link :href="'https://arxiv.org/abs/' + paper.arxiv_id" target="_blank" style="margin-left:15px">
                在 arXiv 上查看
              </el-link>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { Back, Document } from '@element-plus/icons-vue'

const route = useRoute()
const loading = ref(false)
const paper = ref(null)

const fetchPaperDetail = async (id) => {
  loading.value = true
  // Mock Data
  setTimeout(() => {
    paper.value = {
      id: id,
      arxiv_id: '2403.01234',
      title: 'An Awesome Breakthrough in AI Models',
      authors: ['Alice Smith', 'Bob Johnson', 'Charlie Brown'],
      abstract: 'This paper presents a novel approach to optimizing large language models. By introducing a new attention mechanism, we achieve a 10x speedup in inference time without compromising accuracy. The method is evaluated on standard benchmarks and shows state-of-the-art results.',
      pdf_url: 'https://arxiv.org/pdf/2403.01234.pdf',
      one_line_summary: '这篇论文提出了一种全新方法，让AI的响应速度提升了十倍！',
      core_highlights: [
        '无需增加额外算力，仅靠算法优化实现性能飞跃。',
        '在多个主流评测榜单中刷新了SOTA记录。',
        '开源了完整的训练代码和权重，方便社区复现。',
        '彻底解决了在长文本生成中的显存爆炸问题。'
      ],
      application_scenarios: '这项技术可以直接部署在手机等端侧设备上。未来，你的手机语音助手在回答复杂问题时，将不再需要漫长的“思考时间”，而是能够做到即问即答。同时，对于企业来说，这也意味着大模型推理成本的成倍降低。',
      issue_date: '2026-03-23',
      arxiv_publish_date: '2026-03-22'
    }
    loading.value = false
  }, 500)
}

onMounted(() => {
  fetchPaperDetail(route.params.id)
})
</script>

<style scoped>
.page-header {
  margin-bottom: 20px;
}

.article-title {
  font-size: 24px;
  color: #303133;
  margin-top: 0;
  margin-bottom: 15px;
  line-height: 1.4;
}

.article-meta {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 30px;
  color: #909399;
  font-size: 14px;
}

.ai-summary-section {
  background-color: #ffffff;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  margin-bottom: 30px;
}

.highlight-alert {
  margin-bottom: 25px;
}

.highlight-alert :deep(.el-alert__title) {
  font-size: 16px;
  font-weight: bold;
}

.highlight-alert :deep(.el-alert__description) {
  font-size: 15px;
  margin-top: 8px;
  line-height: 1.5;
}

.section-block {
  margin-bottom: 25px;
}

.section-block h3 {
  color: #303133;
  font-size: 18px;
  margin-bottom: 12px;
}

.section-block ul {
  padding-left: 20px;
  color: #606266;
  line-height: 1.8;
  font-size: 15px;
}

.section-block p {
  color: #606266;
  line-height: 1.8;
  font-size: 15px;
}

.original-section {
  background-color: #ffffff;
  border-radius: 8px;
  padding: 10px 20px;
}

.abstract-text {
  color: #606266;
  line-height: 1.6;
  font-style: italic;
  margin-bottom: 20px;
}

.pdf-link {
  display: flex;
  align-items: center;
}
</style>
