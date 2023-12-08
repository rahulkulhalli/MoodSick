<template>
  <h1>
    Aggregate Input Ratings
  </h1>
  <div id="main" style="height:80vh; width:80vw">

  </div>
</template>

<script>
import * as echarts from 'echarts';

export default {
  mounted() {
    var chartDom = document.getElementById('main');
    var myChart = echarts.init(chartDom);
    var option;
    let xAxisColum = ['rock', 'disco', 'pop', 'blues', 'metal']

    option = {
      xAxis: {
        type: 'category',
        name: 'Aggregate Input Ratings',
        data: xAxisColum
      },
      yAxis: {
        type: 'value',
        name: 'Aggregate Values',
      },

      series: [
        {
          data: [0.45900342, 0.06211936, 0.18661687, 0.0138607, 0.27839965],
          type: 'bar'
        }
      ]
    };

    option && myChart.setOption(option);

  }
}
</script>

<style></style>