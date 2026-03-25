import { ElementPlus, createMemoryHistory, createRouter } from '../../frontend/test-utils.js'

export const flushPromises = () => new Promise((resolve) => setTimeout(resolve, 0))

export const testPlugins = [ElementPlus]

export async function createTestRouter(routePath, routeLocation, component) {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [{ path: routePath, component }]
  })

  await router.push(routeLocation)
  await router.isReady()
  return router
}
