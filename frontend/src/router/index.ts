import { createRouter, createWebHistory } from 'vue-router'
import Upload from '../views/Upload.vue'
import Share from '../views/Share.vue'
import Movie from '../views/Movie.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'upload',
      component: Upload
    },
    {
      path: '/share/:hash',
      name: 'share',
      component: Share
    },
    {
      path: '/movie/:hash',
      name: 'movie',
      component: Movie
    }
  ]
})

export default router