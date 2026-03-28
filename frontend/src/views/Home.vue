<template>
  <div class="home-page">
    <div class="page-header">
      <div class="header-copy">
        <h2 v-if="lang === 'cn'">最新简报</h2>
        <h2 v-else>Latest Briefings</h2>
        <p class="subtitle">
          {{ lang === 'cn'
            ? '每日从数百篇前沿AI论文中产出最多5篇Focus与最多12篇Watching，实际数量取决于当日供给与生成结果。每页仅展示一天内容。右侧日历可快速跳转；无数据日期会显示为灰色。'
            : 'Each issue produces up to 5 Focus papers and up to 12 Watching papers from hundreds of frontier AI papers, and the actual count depends on daily supply and generation results. Each page shows one issue date only. Use the calendar on the right for quick jumps; dates without data are shown in gray.' }}
        </p>
      </div>
      <el-button class="topics-entry-button" type="primary" plain @click="goToTopics">
        {{ lang === 'cn' ? '进入论文分类' : 'Browse Categories' }}
      </el-button>
    </div>

    <div class="home-layout">
      <section class="day-panel">
        <el-divider content-position="left">
          <span class="group-date">{{ selectedDate || '--' }}</span>
          <el-link
            v-if="selectedDate"
            :underline="false"
            class="source-link"
            @click="goToSources(selectedDate)"
          >
            {{ lang === 'cn' ? '查看原始候选池' : 'View Candidate Pool' }}
          </el-link>
        </el-divider>

        <div v-if="loading" class="loading-state">
          <el-skeleton :rows="6" animated />
          <el-skeleton :rows="4" animated style="margin-top: 20px" />
        </div>

        <div v-else-if="!selectedGroup.focus.length && !selectedGroup.watching.length" class="empty-state">
          <el-empty :description="lang === 'cn' ? `当天暂无可展示内容（${selectedDate || '未选择日期'}）` : `No displayable briefs for ${selectedDate || 'selected date'}`" />
        </div>

        <div v-else class="paper-feed">
          <div class="focus-section">
            <div class="section-title">
              <el-tag type="danger" effect="dark" round>Focus</el-tag>
              <span class="title-text">{{ lang === 'cn' ? '重点关注' : 'Top Recommendations' }}</span>
            </div>

            <el-card
              v-for="paper in selectedGroup.focus"
              :key="paper.id"
              class="paper-card focus-card"
              shadow="hover"
            >
              <template #header>
                <div class="card-header">
                  <div class="title-area">
                    <el-tag size="small" effect="plain" class="direction-tag">{{ paper.direction }}</el-tag>
                    <h3 class="paper-title" @click="goToDetail(paper.id)">
                      {{ lang === 'cn' ? paper.title_zh : paper.title_original }}
                    </h3>
                  </div>
                  <div class="score-badge">
                    <span class="score-val">{{ paper.score }}</span>
                    <span class="score-label">PTS</span>
                  </div>
                </div>
              </template>

              <div class="paper-content">
                <div class="summary-box">
                  <p class="one-line">{{ lang === 'cn' ? paper.one_line_summary : paper.one_line_summary_en }}</p>
                </div>
              </div>

              <div class="card-footer">
                <el-button type="primary" @click="goToDetail(paper.id)">
                  {{ lang === 'cn' ? '解读全文' : 'Read Full Brief' }}
                </el-button>
                <el-link :href="'https://arxiv.org/abs/' + paper.arxiv_id" target="_blank" type="info" :underline="false">
                  arXiv:{{ paper.arxiv_id }}
                </el-link>
              </div>
            </el-card>
          </div>

          <div v-if="selectedGroup.watching.length > 0" class="watching-section">
            <div class="section-title">
              <el-tag type="info" effect="dark" round>Watching</el-tag>
              <span class="title-text">{{ lang === 'cn' ? '也值得关注' : 'Also Worth Watching' }}</span>
            </div>

            <div class="watching-list">
              <div
                v-for="paper in selectedGroup.watching"
                :key="paper.id"
                class="watching-item"
                @click="goToDetail(paper.id)"
              >
                <div class="wi-header">
                  <span class="wi-direction">[{{ paper.direction }}]</span>
                  <span class="wi-title">{{ lang === 'cn' ? paper.title_zh : paper.title_original }}</span>
                  <span class="wi-score">{{ paper.score }}</span>
                </div>
                <p class="wi-summary">{{ lang === 'cn' ? paper.one_line_summary : paper.one_line_summary_en }}</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <aside class="calendar-panel">
        <div class="calendar-header">
          <button
            type="button"
            class="month-switch"
            :disabled="!canGoPrevMonth"
            @click="goPrevMonth"
          >
            ‹
          </button>
          <span class="month-label">{{ monthLabel }}</span>
          <button
            type="button"
            class="month-switch"
            :disabled="!canGoNextMonth"
            @click="goNextMonth"
          >
            ›
          </button>
        </div>

        <div class="weekday-row">
          <span v-for="weekday in weekdayLabels" :key="weekday" class="weekday-label">{{ weekday }}</span>
        </div>

        <div class="calendar-grid">
          <button
            v-for="cell in calendarCells"
            :key="cell.key"
            type="button"
            class="calendar-cell"
            :class="{
              empty: !cell.dateKey,
              selected: cell.isSelected,
              'has-data': cell.hasData,
              'no-data': cell.dateKey && !cell.hasData,
              disabled: !cell.inRange,
            }"
            :disabled="!cell.dateKey || !cell.inRange || loading"
            @click="selectDate(cell.dateKey)"
          >
            <span v-if="cell.dateKey">{{ cell.day }}</span>
          </button>
        </div>

        <div class="calendar-legend">
          <span class="legend-item">
            <span class="legend-dot has-data-dot" />
            {{ lang === 'cn' ? '有数据' : 'Has Data' }}
          </span>
          <span class="legend-item">
            <span class="legend-dot no-data-dot" />
            {{ lang === 'cn' ? '无数据' : 'No Data' }}
          </span>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { computed, inject, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getPapers, getPapersCalendar } from '../api/papers'

const lang = inject('lang')
const router = useRouter()
const route = useRoute()

const loading = ref(false)
const selectedDate = ref('')
const selectedGroup = ref({ date: '', focus: [], watching: [] })

const minIssueDate = ref('')
const maxIssueDate = ref('')
const latestWithContent = ref('')
const calendarDays = ref([])
const calendarMonth = ref('')

let currentRequestId = 0

const weekdayLabels = computed(() => (
  lang.value === 'cn'
    ? ['一', '二', '三', '四', '五', '六', '日']
    : ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
))

const dateStateMap = computed(() => {
  const map = new Map()
  calendarDays.value.forEach((day) => {
    map.set(day.issue_date, day)
  })
  return map
})

const monthLabel = computed(() => {
  if (!calendarMonth.value) return '--'
  const [year, month] = calendarMonth.value.split('-').map(Number)
  return lang.value === 'cn' ? `${year} 年 ${month} 月` : `${year}-${String(month).padStart(2, '0')}`
})

const canGoPrevMonth = computed(() => {
  if (!calendarMonth.value || !minIssueDate.value) return false
  return calendarMonth.value > minIssueDate.value.slice(0, 7)
})

const canGoNextMonth = computed(() => {
  if (!calendarMonth.value || !maxIssueDate.value) return false
  return calendarMonth.value < maxIssueDate.value.slice(0, 7)
})

const calendarCells = computed(() => {
  if (!calendarMonth.value) return []
  const [year, month] = calendarMonth.value.split('-').map(Number)
  const firstDay = new Date(year, month - 1, 1)
  const daysInMonth = new Date(year, month, 0).getDate()
  const startOffset = (firstDay.getDay() + 6) % 7

  const cells = []
  for (let i = 0; i < startOffset; i += 1) {
    cells.push({ key: `empty-${i}`, dateKey: '', day: '', hasData: false, inRange: false, isSelected: false })
  }

  for (let day = 1; day <= daysInMonth; day += 1) {
    const dateKey = toDateKey(new Date(year, month - 1, day))
    const state = dateStateMap.value.get(dateKey)
    const inRange = isDateInRange(dateKey, minIssueDate.value, maxIssueDate.value)
    cells.push({
      key: dateKey,
      dateKey,
      day,
      hasData: !!state?.has_content,
      inRange,
      isSelected: selectedDate.value === dateKey,
    })
  }

  while (cells.length % 7 !== 0) {
    cells.push({
      key: `empty-tail-${cells.length}`,
      dateKey: '',
      day: '',
      hasData: false,
      inRange: false,
      isSelected: false,
    })
  }
  return cells
})

function toDateKey(value) {
  const year = value.getFullYear()
  const month = String(value.getMonth() + 1).padStart(2, '0')
  const day = String(value.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function parseDateKey(dateKey) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(dateKey)) return null
  const [year, month, day] = dateKey.split('-').map(Number)
  return new Date(year, month - 1, day)
}

function shiftMonth(monthKey, delta) {
  const [year, month] = monthKey.split('-').map(Number)
  const shifted = new Date(year, month - 1 + delta, 1)
  return toDateKey(shifted).slice(0, 7)
}

function isDateInRange(dateKey, minDate, maxDate) {
  if (!dateKey) return false
  if (minDate && dateKey < minDate) return false
  if (maxDate && dateKey > maxDate) return false
  return true
}

function buildSelectedGroup(items, dateKey) {
  const focus = []
  const watching = []
  items.forEach((paper) => {
    if (paper.category === 'focus') {
      focus.push(paper)
    } else if (paper.category === 'watching') {
      watching.push(paper)
    }
  })
  focus.sort((a, b) => b.score - a.score)
  watching.sort((a, b) => b.score - a.score)
  return { date: dateKey, focus, watching }
}

async function fetchCalendar() {
  try {
    const calendar = await getPapersCalendar()
    const days = Array.isArray(calendar.days) ? calendar.days : []
    calendarDays.value = days
    minIssueDate.value = calendar.min_issue_date || ''
    maxIssueDate.value = calendar.max_issue_date || ''
    latestWithContent.value = calendar.latest_with_content || ''

    const routeDate = typeof route.query.date === 'string' ? route.query.date : ''
    const defaultDate = routeDate || latestWithContent.value || maxIssueDate.value || ''
    if (!defaultDate) return

    if (!isDateInRange(defaultDate, minIssueDate.value, maxIssueDate.value)) {
      return
    }

    calendarMonth.value = defaultDate.slice(0, 7)
    if (routeDate !== defaultDate) {
      router.replace({ query: { ...route.query, date: defaultDate } })
    } else {
      selectedDate.value = defaultDate
      await fetchPapersByDate(defaultDate)
    }
  } catch (error) {
    calendarDays.value = []
    selectedGroup.value = { date: '', focus: [], watching: [] }
  }
}

async function fetchPapersByDate(issueDate) {
  if (!issueDate) return
  loading.value = true
  const requestId = ++currentRequestId
  try {
    const data = await getPapers({ page: 1, limit: 100, issue_date: issueDate })
    if (requestId !== currentRequestId) return
    selectedGroup.value = buildSelectedGroup(data.items || [], issueDate)
  } catch (error) {
    if (requestId !== currentRequestId) return
    selectedGroup.value = { date: issueDate, focus: [], watching: [] }
  } finally {
    if (requestId === currentRequestId) {
      loading.value = false
    }
  }
}

function selectDate(dateKey) {
  if (!dateKey || !isDateInRange(dateKey, minIssueDate.value, maxIssueDate.value)) return
  if (dateKey === selectedDate.value) return
  router.replace({ query: { ...route.query, date: dateKey } })
}

function goPrevMonth() {
  if (!canGoPrevMonth.value) return
  calendarMonth.value = shiftMonth(calendarMonth.value, -1)
}

function goNextMonth() {
  if (!canGoNextMonth.value) return
  calendarMonth.value = shiftMonth(calendarMonth.value, 1)
}

function goToDetail(id) {
  router.push(`/paper/${id}`)
}

function goToSources(issueDate) {
  if (!issueDate) return
  router.push(`/sources/${issueDate}`)
}

function goToTopics() {
  router.push('/topics')
}

onMounted(() => {
  fetchCalendar()
})

watch(() => route.query.date, (newDate) => {
  const nextDate = typeof newDate === 'string' ? newDate : ''
  if (!nextDate || !isDateInRange(nextDate, minIssueDate.value, maxIssueDate.value)) return
  selectedDate.value = nextDate
  const parsed = parseDateKey(nextDate)
  if (parsed) {
    calendarMonth.value = toDateKey(parsed).slice(0, 7)
  }
  fetchPapersByDate(nextDate)
})
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.header-copy h2 {
  margin: 0;
  color: #303133;
  font-size: 24px;
}

.subtitle {
  margin: 8px 0 0 0;
  color: #909399;
  font-size: 15px;
}

.topics-entry-button {
  flex-shrink: 0;
  margin-left: 16px;
}

.home-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 320px;
  gap: 24px;
  align-items: start;
}

.day-panel {
  min-width: 0;
}

.group-date {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.source-link {
  margin-left: 15px;
  font-size: 13px;
  font-weight: normal;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 18px;
}

.title-text {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.focus-section {
  margin-bottom: 32px;
}

.paper-card {
  margin-bottom: 20px;
  border-radius: 12px;
  border: 1px solid #ebeef5;
  transition: all 0.3s cubic-bezier(.25,.8,.25,1);
}

.focus-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.05);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.title-area {
  flex: 1;
}

.direction-tag {
  margin-bottom: 8px;
}

.paper-title {
  margin: 0;
  font-size: 20px;
  color: #1a1a1a;
  cursor: pointer;
  line-height: 1.4;
}

.paper-title:hover {
  color: #409eff;
}

.score-badge {
  background: #fdf6ec;
  border: 1px solid #faecd8;
  color: #e6a23c;
  padding: 5px 10px;
  border-radius: 8px;
  text-align: center;
  margin-left: 15px;
}

.score-val {
  display: block;
  font-size: 18px;
  font-weight: bold;
}

.score-label {
  font-size: 10px;
  opacity: 0.8;
}

.summary-box {
  background-color: #f0f9eb;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  border-left: 4px solid #67c23a;
}

.one-line {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
  color: #2c3e50;
  line-height: 1.6;
}

.card-footer {
  margin-top: 22px;
  display: flex;
  align-items: center;
  gap: 20px;
}

.watching-list {
  background: #fff;
  border-radius: 12px;
  border: 1px solid #ebeef5;
  overflow: hidden;
}

.watching-item {
  padding: 14px 18px;
  border-bottom: 1px solid #f0f2f5;
  cursor: pointer;
  transition: background 0.2s;
}

.watching-item:last-child {
  border-bottom: none;
}

.watching-item:hover {
  background-color: #f9fbff;
}

.wi-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 5px;
}

.wi-direction {
  color: #909399;
  font-size: 13px;
  font-family: monospace;
}

.wi-title {
  font-weight: bold;
  color: #303133;
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.wi-score {
  font-size: 12px;
  color: #e6a23c;
  font-weight: bold;
}

.wi-summary {
  margin: 0;
  font-size: 14px;
  color: #606266;
}

.calendar-panel {
  position: sticky;
  top: 16px;
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 12px;
  padding: 14px;
}

.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.month-label {
  font-weight: 600;
  color: #303133;
}

.month-switch {
  width: 30px;
  height: 30px;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  background: #fff;
  color: #606266;
  cursor: pointer;
}

.month-switch:disabled {
  cursor: not-allowed;
  color: #c0c4cc;
  background: #f5f7fa;
}

.weekday-row {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 6px;
  margin-bottom: 8px;
}

.weekday-label {
  text-align: center;
  font-size: 12px;
  color: #909399;
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 6px;
}

.calendar-cell {
  height: 34px;
  border-radius: 8px;
  border: 1px solid transparent;
  background: #f9fafc;
  color: #606266;
  cursor: pointer;
  font-size: 13px;
}

.calendar-cell.empty {
  background: transparent;
  cursor: default;
}

.calendar-cell.has-data {
  background: #ecf5ff;
  color: #303133;
}

.calendar-cell.no-data {
  background: #f2f3f5;
  color: #b4b8bf;
}

.calendar-cell.selected {
  border-color: #409eff;
  background: #409eff;
  color: #fff;
  font-weight: 600;
}

.calendar-cell.disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.calendar-legend {
  margin-top: 12px;
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #909399;
}

.legend-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
}

.has-data-dot {
  background: #409eff;
}

.no-data-dot {
  background: #c0c4cc;
}

@media (max-width: 992px) {
  .home-layout {
    grid-template-columns: 1fr;
  }

  .calendar-panel {
    position: static;
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 16px;
  }

  .topics-entry-button {
    margin-left: 0;
    width: 100%;
  }
}
</style>
