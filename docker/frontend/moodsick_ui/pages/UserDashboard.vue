<template>
  <ClientOnly>
    <FirstLogin v-if="login_type=='first'"></FirstLogin>
  </ClientOnly>
</template>

<script>
export default {
  data(){
    return {
      user_data: sessionStorage.getItem("user_data"),
      login_type: null
    }
  },
  created(){
    if (this.user_data == null ){
      this.$router.push("/Login")
      return
    } 
  },
  mounted(){
    
    if (Boolean(this.user_data.login_history) && this.user_data.login_history.length > 1){

    } else {
      this.login_type = 'first';
    }

  }
};
</script>

<style>
</style>