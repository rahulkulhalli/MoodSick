<template>
  <div>
    <!-- <NuxtWelcome /> -->
    <TopNavbar v-if="!['Login','Register'].includes($route.name)"></TopNavbar>
    <NuxtPage />
    <!-- <Login></Login> -->
  </div>
</template>
<script setup>
useHead({
  title: 'MoodSick',
  meta: [
    { name: 'description', content: 'My amazing site.' }
  ],
  bodyAttrs: {
    class: 'test'
  },
  script: [ { innerHTML: 'console.log(\'Hello world\')' } ]
})

  </script>
  <script>
export default {
  mounted(){
    // let cl = ["visual-effects" , "bg-white", "dark:bg-black"]
    // cl.forEach(element => {
    //   document.body.classList.add(element)
    // });
  }
}
</script>

<style>
body {
  background-image: linear-gradient(to right, #b6fbff, #83a4d4);

  
}
</style>