<template>
  <ClientOnly>
    <FirstLogin v-if="login_type=='first'"></FirstLogin>
    <NewFlow v-else></NewFlow>
  </ClientOnly>
</template>

<script>
export default {
  data(){
    return {
      user_data: null,
      login_type: null
    }
  },
  created(){
   
  },
  mounted(){
    this.user_data = JSON.parse(sessionStorage.getItem("user_data"))
    console.log(this.user_data);
    if (this.user_data == null ){
      this.$router.push("/Login")
      return
    } 
    console.log(this.user_data.login_history.length);
    if (Boolean(this.user_data.login_history) && this.user_data.login_history.length > 1){

    } else {
      this.login_type = 'first';
    }

  }
};
</script>

<style>
</style>