import { ref } from 'vue'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { mount } from '../../frontend/test-utils.js'

import { candidateDetail, focusDetail } from '../fixtures/frontend-data'
import { createTestRouter, flushPromises, testPlugins } from './helpers'
const getPaperDetailMock = vi.fn()

vi.mock('../../frontend/src/api/papers', () => ({
  getPaperDetail: (...args) => getPaperDetailMock(...args)
}))

import Detail from '../../frontend/src/views/Detail.vue'

describe('Detail view', () => {
  beforeEach(() => {
    getPaperDetailMock.mockReset()
  })

  it('renders narrative sections for non-candidate papers', async () => {
    getPaperDetailMock.mockResolvedValue(focusDetail)
    const router = await createTestRouter('/paper/:id', '/paper/1', Detail)

    const wrapper = mount(Detail, {
      global: {
        provide: { lang: ref('cn') },
        plugins: [...testPlugins, router]
      }
    })

    await flushPromises()

    expect(wrapper.text()).toContain('中文焦点标题')
    expect(wrapper.text()).toContain('焦点中文总结')
    expect(wrapper.text()).toContain('亮点一')
    expect(wrapper.text()).not.toContain('候选池')
  })

  it('renders candidate fallback without AI narrative content', async () => {
    getPaperDetailMock.mockResolvedValue(candidateDetail)
    const router = await createTestRouter('/paper/:id', '/paper/4', Detail)

    const wrapper = mount(Detail, {
      global: {
        provide: { lang: ref('cn') },
        plugins: [...testPlugins, router]
      }
    })

    await flushPromises()

    expect(wrapper.text()).toContain('最新候选标题')
    expect(wrapper.text()).toContain('容量溢出')
    expect(wrapper.text()).toContain('候选池')
    expect(wrapper.text()).not.toContain('亮点一')
  })
})
