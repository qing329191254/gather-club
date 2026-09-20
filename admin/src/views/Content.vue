<template>
  <div class="content-page">
    <el-tabs v-model="tab" @tab-change="onTabChange">
      <el-tab-pane label="协议文案" name="agreements" />
      <el-tab-pane label="收集清单" name="privacy_collect" />
      <el-tab-pane label="共享清单" name="privacy_share" />
      <el-tab-pane label="会员配置" name="member" />
    </el-tabs>

    <div v-loading="loading" class="pane">
      <!-- 协议 -->
      <template v-if="tab === 'agreements'">
        <div class="toolbar">
          <el-radio-group :model-value="agreeKey" @change="onAgreeKeyChange">
            <el-radio-button value="privacy">用户隐私协议</el-radio-button>
            <el-radio-button value="cancel">注销账号协议</el-radio-button>
          </el-radio-group>
        </div>
        <el-form label-width="100px" class="form">
          <el-form-item label="导航标题">
            <el-input v-model="agreeDoc.navTitle" placeholder="小程序顶部标题" />
          </el-form-item>
          <el-form-item label="协议标题">
            <el-input v-model="agreeDoc.title" placeholder="正文大标题" />
          </el-form-item>
          <el-form-item label="开头说明">
            <el-input v-model="agreeDoc.intro" type="textarea" :rows="4" placeholder="协议开头导语" />
          </el-form-item>
          <el-form-item label="结尾确认">
            <el-input v-model="agreeDoc.confirm" type="textarea" :rows="3" placeholder="可选，文末确认声明" />
          </el-form-item>
        </el-form>

        <div class="section-head">
          <h3>正文章节</h3>
          <el-button type="primary" size="small" @click="addBlock">新增章节</el-button>
        </div>
        <div v-for="(block, bi) in agreeDoc.blocks" :key="block._key" class="card">
          <div class="card-head">
            <strong>章节 {{ bi + 1 }}</strong>
            <el-button link type="danger" @click="agreeDoc.blocks.splice(bi, 1)">删除</el-button>
          </div>
          <el-form label-width="90px">
            <el-form-item label="章节标题">
              <el-input v-model="block.heading" placeholder="例如：一、账号注销后果" />
            </el-form-item>
            <el-form-item label="段落">
              <div class="lines">
                <div v-for="(p, pi) in block.paras" :key="pi" class="line-row">
                  <el-input v-model="block.paras[pi]" type="textarea" :rows="2" placeholder="段落文字" />
                  <el-button link type="danger" @click="block.paras.splice(pi, 1)">删</el-button>
                </div>
                <el-button size="small" @click="block.paras.push('')">+ 加一段</el-button>
              </div>
            </el-form-item>
            <el-form-item label="小节">
              <div class="subs">
                <div v-for="(sub, si) in block.subs" :key="sub._key" class="sub-card">
                  <div class="card-head">
                    <span>小节 {{ si + 1 }}</span>
                    <el-button link type="danger" @click="block.subs.splice(si, 1)">删除</el-button>
                  </div>
                  <el-input v-model="sub.title" placeholder="小节标题，如 1.1 xxx" class="mb8" />
                  <div v-for="(sp, spi) in sub.paras" :key="spi" class="line-row">
                    <el-input v-model="sub.paras[spi]" type="textarea" :rows="2" />
                    <el-button link type="danger" @click="sub.paras.splice(spi, 1)">删</el-button>
                  </div>
                  <el-button size="small" @click="sub.paras.push('')">+ 加一段</el-button>
                </div>
                <el-button size="small" @click="addSub(block)">+ 加小节</el-button>
              </div>
            </el-form-item>
          </el-form>
        </div>
      </template>

      <!-- 收集清单 -->
      <template v-else-if="tab === 'privacy_collect'">
        <el-form label-width="100px" class="form">
          <el-form-item label="开头说明">
            <el-input v-model="collect.intro" type="textarea" :rows="4" />
          </el-form-item>
        </el-form>
        <div class="section-head">
          <h3>收集条目</h3>
          <el-button type="primary" size="small" @click="addCollectItem">新增条目</el-button>
        </div>
        <div v-for="(item, i) in collect.sections" :key="item._key" class="card">
          <div class="card-head">
            <strong>条目 {{ i + 1 }}</strong>
            <el-button link type="danger" @click="collect.sections.splice(i, 1)">删除</el-button>
          </div>
          <el-form label-width="100px">
            <el-form-item label="场景标题"><el-input v-model="item.title" placeholder="例如：账号注册与登录" /></el-form-item>
            <el-form-item label="收集内容"><el-input v-model="item.content" placeholder="例如：微信头像、昵称、手机号" /></el-form-item>
            <el-form-item label="使用目的"><el-input v-model="item.purpose" /></el-form-item>
            <el-form-item label="使用场景"><el-input v-model="item.scene" /></el-form-item>
          </el-form>
        </div>
      </template>

      <!-- 共享清单 -->
      <template v-else-if="tab === 'privacy_share'">
        <el-form label-width="100px" class="form">
          <el-form-item label="开头说明">
            <el-input v-model="share.intro" type="textarea" :rows="4" />
          </el-form-item>
        </el-form>
        <div class="section-head">
          <h3>共享条目</h3>
          <el-button type="primary" size="small" @click="addShareItem">新增条目</el-button>
        </div>
        <div v-for="(item, i) in share.sections" :key="item._key" class="card">
          <div class="card-head">
            <strong>条目 {{ i + 1 }}</strong>
            <el-button link type="danger" @click="share.sections.splice(i, 1)">删除</el-button>
          </div>
          <el-form label-width="100px">
            <el-form-item label="能力名称"><el-input v-model="item.title" placeholder="例如：微信支付" /></el-form-item>
            <el-form-item label="第三方名称"><el-input v-model="item.name" /></el-form-item>
            <el-form-item label="共享信息"><el-input v-model="item.info" type="textarea" :rows="2" /></el-form-item>
            <el-form-item label="使用目的"><el-input v-model="item.purpose" /></el-form-item>
            <el-form-item label="使用场景"><el-input v-model="item.scene" /></el-form-item>
            <el-form-item label="共享方式"><el-input v-model="item.method" placeholder="例如：接口调用" /></el-form-item>
          </el-form>
        </div>
      </template>

      <!-- 会员 -->
      <template v-else-if="tab === 'member'">
        <el-divider content-position="left">月度券包展示</el-divider>
        <el-form label-width="100px" class="form">
          <el-form-item label="券标题"><el-input v-model="member.monthCoupon.title" /></el-form-item>
          <el-form-item label="使用提示"><el-input v-model="member.monthCoupon.tip" /></el-form-item>
          <el-form-item label="角标文案">
            <el-input v-model="member.monthCoupon.tag" type="textarea" :rows="2" placeholder="可换行，展示在券角标" />
          </el-form-item>
        </el-form>

        <el-divider content-position="left">会员等级</el-divider>
        <el-tabs v-model="levelTab" type="card">
          <el-tab-pane v-for="lv in member.levels" :key="lv.id" :label="lv.id" :name="lv.id">
            <el-form label-width="110px" class="form">
              <el-form-item label="升级所需桌数">
                <el-input-number v-model="lv.need" :min="0" />
              </el-form-item>
              <el-form-item label="进度说明">
                <el-input v-model="lv.needText" placeholder="例如：有效期内完成1桌可升级" />
              </el-form-item>
              <el-form-item label="进度条文案">
                <el-input v-model="lv.progressLabel" placeholder="例如：升级进度" />
              </el-form-item>
              <el-form-item label="已达标展示">
                <el-switch v-model="lv.doneText" active-text="是" inactive-text="否" />
              </el-form-item>
              <el-form-item label="页面背景图">
                <ImageField v-model="lv.pageBgImage" folder="member" />
              </el-form-item>
              <el-form-item label="卡片背景图">
                <ImageField v-model="lv.cardBgImage" folder="member" />
              </el-form-item>
              <el-form-item label="等级图标">
                <ImageField v-model="lv.crownIcon" folder="member" />
              </el-form-item>
            </el-form>
            <div class="section-head">
              <h3>权益列表</h3>
              <el-button type="primary" size="small" @click="addBenefit(lv)">新增权益</el-button>
            </div>
            <div v-for="(b, bi) in lv.benefits" :key="b._key" class="card">
              <div class="card-head">
                <strong>权益 {{ bi + 1 }}</strong>
                <el-button link type="danger" @click="lv.benefits.splice(bi, 1)">删除</el-button>
              </div>
              <el-form label-width="80px">
                <el-form-item label="标题"><el-input v-model="b.title" /></el-form-item>
                <el-form-item label="说明"><el-input v-model="b.desc" /></el-form-item>
                <el-form-item label="图标"><ImageField v-model="b.icon" folder="member" /></el-form-item>
              </el-form>
            </div>
          </el-tab-pane>
        </el-tabs>

        <el-divider content-position="left">会员章程</el-divider>
        <div class="section-head">
          <h3>章程章节</h3>
          <el-button type="primary" size="small" @click="addRuleSection">新增章节</el-button>
        </div>
        <div v-for="(rule, ri) in member.rules" :key="rule._key" class="card">
          <div class="card-head">
            <strong>章节 {{ ri + 1 }}</strong>
            <el-button link type="danger" @click="member.rules.splice(ri, 1)">删除</el-button>
          </div>
          <el-form label-width="90px">
            <el-form-item label="章节标题">
              <el-input v-model="rule.title" placeholder="例如：一、会员等级体系" />
            </el-form-item>
          </el-form>
          <div v-for="(blk, bki) in rule.blocks" :key="blk._key" class="sub-card">
            <div class="card-head">
              <span>小节 {{ bki + 1 }}</span>
              <el-button link type="danger" @click="rule.blocks.splice(bki, 1)">删除</el-button>
            </div>
            <el-input v-model="blk.subtitle" placeholder="小节标题" class="mb8" />
            <div v-for="(para, pi) in blk.paras" :key="pi" class="para-edit">
              <el-input v-model="para.text" type="textarea" :rows="2" placeholder="段落内容" />
              <div class="para-flags">
                <el-checkbox v-model="para.indent">缩进</el-checkbox>
                <el-checkbox v-model="para.tip">备注样式</el-checkbox>
                <el-button link type="danger" @click="blk.paras.splice(pi, 1)">删除</el-button>
              </div>
            </div>
            <el-button size="small" @click="blk.paras.push({ text: '', indent: false, tip: false })">+ 加一段</el-button>
          </div>
          <el-button size="small" class="mt8" @click="addRuleBlock(rule)">+ 加小节</el-button>
        </div>
      </template>
    </div>

    <div class="actions">
      <el-button type="primary" :loading="saving" @click="onSave">保存当前页</el-button>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../api/http'
import ImageField from '../components/ImageField.vue'

const tab = ref('agreements')
const loading = ref(false)
const saving = ref(false)
let uid = 1
const keyOf = () => `k${uid++}`

const agreeKey = ref('privacy')
const agreementsRaw = ref({})
const agreeDoc = reactive({
  navTitle: '',
  title: '',
  intro: '',
  confirm: '',
  blocks: []
})

const collect = reactive({ intro: '', sections: [] })
const share = reactive({ intro: '', sections: [] })

const levelTab = ref('V0')
const member = reactive({
  levels: [],
  monthCoupon: { title: '', tip: '', tag: '' },
  rules: []
})

function normalizeParas(list) {
  return (list || []).map((p) => (typeof p === 'string' ? p : String(p ?? '')))
}

function normalizeBlock(block = {}) {
  return {
    _key: keyOf(),
    heading: block.heading || '',
    paras: normalizeParas(block.paras),
    subs: (block.subs || []).map((s) => ({
      _key: keyOf(),
      title: s.title || '',
      paras: normalizeParas(s.paras)
    }))
  }
}

function loadAgreementDoc() {
  const doc = agreementsRaw.value[agreeKey.value] || {}
  agreeDoc.navTitle = doc.navTitle || ''
  agreeDoc.title = doc.title || ''
  agreeDoc.intro = doc.intro || ''
  agreeDoc.confirm = doc.confirm || ''
  agreeDoc.blocks = (doc.blocks || []).map(normalizeBlock)
}

function addBlock() {
  agreeDoc.blocks.push(normalizeBlock({ heading: '', paras: [''], subs: [] }))
}

function addSub(block) {
  block.subs.push({ _key: keyOf(), title: '', paras: [''] })
}

function addCollectItem() {
  collect.sections.push({ _key: keyOf(), title: '', content: '', purpose: '', scene: '' })
}

function addShareItem() {
  share.sections.push({
    _key: keyOf(),
    title: '',
    name: '',
    info: '',
    purpose: '',
    scene: '',
    method: ''
  })
}

function addBenefit(lv) {
  lv.benefits.push({ _key: keyOf(), title: '', desc: '', icon: '' })
}

function addRuleSection() {
  member.rules.push({
    _key: keyOf(),
    title: '',
    blocks: [{ _key: keyOf(), subtitle: '', paras: [{ text: '', indent: false, tip: false }] }]
  })
}

function addRuleBlock(rule) {
  rule.blocks.push({
    _key: keyOf(),
    subtitle: '',
    paras: [{ text: '', indent: false, tip: false }]
  })
}

function normalizeRulePara(p) {
  if (typeof p === 'string') return { text: p, indent: false, tip: false }
  return {
    text: p?.text || '',
    indent: !!p?.indent,
    tip: !!p?.tip
  }
}

async function loadCurrent() {
  loading.value = true
  try {
    const res = await http.get(`/config/${tab.value}`)
    const value = res.value || {}
    if (tab.value === 'agreements') {
      agreementsRaw.value = value
      if (!agreementsRaw.value[agreeKey.value]) {
        agreeKey.value = Object.keys(agreementsRaw.value)[0] || 'privacy'
      }
      loadAgreementDoc()
    } else if (tab.value === 'privacy_collect') {
      collect.intro = value.intro || ''
      collect.sections = (value.sections || []).map((s) => ({
        _key: keyOf(),
        title: s.title || '',
        content: s.content || '',
        purpose: s.purpose || '',
        scene: s.scene || ''
      }))
    } else if (tab.value === 'privacy_share') {
      share.intro = value.intro || ''
      share.sections = (value.sections || []).map((s) => ({
        _key: keyOf(),
        title: s.title || '',
        name: s.name || '',
        info: s.info || '',
        purpose: s.purpose || '',
        scene: s.scene || '',
        method: s.method || ''
      }))
    } else if (tab.value === 'member') {
      member.monthCoupon = {
        title: value.monthCoupon?.title || '',
        tip: value.monthCoupon?.tip || '',
        tag: value.monthCoupon?.tag || ''
      }
      member.levels = (value.levels || []).map((lv) => ({
        ...lv,
        benefits: (lv.benefits || []).map((b) => ({
          _key: keyOf(),
          title: b.title || '',
          desc: b.desc || '',
          icon: b.icon || ''
        }))
      }))
      levelTab.value = member.levels[0]?.id || 'V0'
      member.rules = (value.rules || []).map((r) => ({
        _key: keyOf(),
        title: r.title || '',
        blocks: (r.blocks || []).map((b) => ({
          _key: keyOf(),
          subtitle: b.subtitle || '',
          paras: (b.paras || []).map(normalizeRulePara)
        }))
      }))
    }
  } finally {
    loading.value = false
  }
}

function stashAgreementDoc(key = agreeKey.value) {
  const next = { ...agreementsRaw.value }
  next[key] = {
    navTitle: agreeDoc.navTitle.trim(),
    title: agreeDoc.title.trim(),
    intro: agreeDoc.intro,
    confirm: agreeDoc.confirm,
    blocks: agreeDoc.blocks.map((b) => ({
      heading: b.heading.trim(),
      paras: (b.paras || []).map((p) => String(p || '').trim()).filter(Boolean),
      subs: (b.subs || []).map((s) => ({
        title: s.title.trim(),
        paras: (s.paras || []).map((p) => String(p || '').trim()).filter(Boolean)
      }))
    }))
  }
  agreementsRaw.value = next
}

function onAgreeKeyChange(nextKey) {
  stashAgreementDoc(agreeKey.value)
  agreeKey.value = nextKey
  loadAgreementDoc()
}

async function onTabChange() {
  // 切 Tab 前先把当前页写入服务器，避免上传/改文案后丢掉
  try {
    await onSave(false)
  } catch {
    /* ignore */
  }
  loadCurrent()
}

function buildAgreementPayload() {
  stashAgreementDoc(agreeKey.value)
  return { ...agreementsRaw.value }
}

function buildMemberPayload() {
  return {
    monthCoupon: { ...member.monthCoupon },
    levels: member.levels.map((lv) => {
      const { benefits, ...rest } = lv
      return {
        ...rest,
        benefits: (benefits || []).map(({ title, desc, icon }) => ({ title, desc, icon }))
      }
    }),
    rules: member.rules.map((r) => ({
      title: r.title,
      blocks: (r.blocks || []).map((b) => ({
        subtitle: b.subtitle,
        paras: (b.paras || [])
          .filter((p) => (p.text || '').trim())
          .map((p) => {
            if (p.tip || p.indent) {
              const out = { text: p.text.trim() }
              if (p.tip) out.tip = true
              if (p.indent) out.indent = true
              return out
            }
            return p.text.trim()
          })
      }))
    }))
  }
}

async function onSave(showToast = true) {
  saving.value = true
  try {
    let value
    if (tab.value === 'agreements') value = buildAgreementPayload()
    else if (tab.value === 'privacy_collect') {
      value = {
        intro: collect.intro,
        sections: collect.sections.map(({ title, content, purpose, scene }) => ({
          title,
          content,
          purpose,
          scene
        }))
      }
    } else if (tab.value === 'privacy_share') {
      value = {
        intro: share.intro,
        sections: share.sections.map(({ title, name, info, purpose, scene, method }) => ({
          title,
          name,
          info,
          purpose,
          scene,
          method
        }))
      }
    } else value = buildMemberPayload()

    await http.put(`/config/${tab.value}`, { value })
    if (tab.value === 'agreements') agreementsRaw.value = value
    if (showToast) ElMessage.success('已保存')
  } finally {
    saving.value = false
  }
}

onMounted(loadCurrent)
</script>

<style scoped>
.content-page {
  background: #fff;
  border-radius: 8px;
  padding: 16px 20px 20px;
}
.pane { min-height: 320px; }
.toolbar { margin-bottom: 16px; }
.form { max-width: 860px; }
.section-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 8px 0 12px;
}
.section-head h3 {
  margin: 0;
  font-size: 15px;
}
.card {
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 12px 14px 4px;
  margin-bottom: 12px;
  background: #fafafa;
}
.card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.sub-card {
  border: 1px dashed #cbd5e1;
  border-radius: 8px;
  padding: 10px;
  margin-bottom: 10px;
  background: #fff;
}
.lines, .subs { width: 100%; }
.line-row {
  display: flex;
  gap: 8px;
  align-items: flex-start;
  margin-bottom: 8px;
}
.line-row .el-input { flex: 1; }
.mb8 { margin-bottom: 8px; }
.mt8 { margin-top: 8px; }
.para-edit {
  margin-bottom: 10px;
}
.para-flags {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 4px;
}
.actions {
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid #e2e8f0;
}
</style>
