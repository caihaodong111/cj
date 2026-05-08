import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'

import {
  ElLoadingDirective,
  ElOption,
  ElSelect,
  ElTable,
  ElTableColumn,
} from 'element-plus'
import 'element-plus/es/components/loading/style/css'
import 'element-plus/es/components/option/style/css'
import 'element-plus/es/components/select/style/css'
import 'element-plus/es/components/table/style/css'
import 'element-plus/es/components/table-column/style/css'

const app = createApp(App)
app.use(router)
app.component(ElSelect.name, ElSelect)
app.component(ElOption.name, ElOption)
app.component(ElTable.name, ElTable)
app.component(ElTableColumn.name, ElTableColumn)
app.directive('loading', ElLoadingDirective)

app.mount('#app')
