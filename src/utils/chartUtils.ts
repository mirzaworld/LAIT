import { Chart } from 'chart.js';
import { Filler } from 'chart.js';

export const registerChartPlugins = () => {
  // Register the Filler plugin if it's not already registered
  if (!Chart.registry.plugins.get('filler')) {
    Chart.register(Filler);
  }
};

// Run the registration immediately
registerChartPlugins();
