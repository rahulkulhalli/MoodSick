// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  devtools: { enabled: true },
  css: [
    'bootstrap/dist/css/bootstrap.css'
  ],
  app: {
    head: {
      
      script: [{ src: 'https://open.spotify.com/embed/iframe-api/v1' }],
    },
  },
 
})
