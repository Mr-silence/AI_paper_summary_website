import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Detail from '../views/Detail.vue'
import Unsubscribe from '../views/Unsubscribe.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home
    },
    {
      path: '/paper/:id',
      name: 'detail',
      component: Detail
    },
    {
      path: '/unsubscribe',
      name: 'unsubscribe',
      component: Unsubscribe
    }
  ]
})

export default router
