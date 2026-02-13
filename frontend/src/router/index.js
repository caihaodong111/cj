import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '../layouts/MainLayout.vue'
import DashboardView from '../views/DashboardView.vue'
import AnalysisView from '../views/AnalysisView.vue'
import DataView from '../views/DataView.vue'
import SettingsView from '../views/SettingsView.vue'

const routes = [
    {
        path: '/',
        component: MainLayout,
        children: [
            {
                path: '',
                redirect: '/dashboard'
            },
            {
                path: 'dashboard',
                name: 'Dashboard',
                component: DashboardView,
                meta: { title: '概览仪表盘' }
            },
            {
                path: 'data',
                name: 'Data',
                component: DataView,
                meta: { title: '数据采集' }
            },
            {
                path: 'analysis',
                name: 'Analysis',
                component: AnalysisView,
                meta: { title: '深度分析' }
            },
            {
                path: 'settings',
                name: 'Settings',
                component: SettingsView,
                meta: { title: '系统设置' }
            }
        ]
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router
