<template>
    <h1>
        Hello
    </h1>
    <div id="main" style="height:80vh; width:80vw">

    </div>
</template>

<script>
import * as echarts from 'echarts';

export default{
    mounted(){
        var chartDom = document.getElementById('main');
var myChart = echarts.init(chartDom);
var option;

option = {
  xAxis: {
    type: 'category',
    name: 'LoginDays',
    data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
  },
  yAxis: {
    type: 'value',
    name: 'Number of times Login',
  },
  
  series: [
    {
      data: [2, 4, 6, 5, 1, 4, 7],
      type: 'bar'
    }
  ]
};

option && myChart.setOption(option);

    }
}
</script>

<style>

</style>