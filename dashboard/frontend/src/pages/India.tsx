import { getIndiaMarketSignals, getIndiaSixMonthCheck, getIndiaReport, getQuarterlyDirection } from "../api";
import Collapsible from "../components/Collapsible";
import ReportSection from "../components/ReportSection";

// India is a separate book (different market, different positions) from the
// 8 US accounts -- stays its own tab rather than folding into US, per the
// real content split already established in the legacy india.html.
export default function IndiaPage() {
  return (
    <div>
      <Collapsible title="Market Signals" defaultOpen>
        <ReportSection fetcher={getIndiaMarketSignals} />
      </Collapsible>
      <Collapsible title="6-Month Plan Tracking" defaultOpen>
        <ReportSection fetcher={getIndiaSixMonthCheck} />
      </Collapsible>
      <Collapsible title="Quarterly Portfolio Direction">
        <ReportSection fetcher={() => getQuarterlyDirection("india").then((text) => ({ text }))} />
      </Collapsible>
      <Collapsible title="Full report / data source detail">
        <ReportSection fetcher={getIndiaReport} />
      </Collapsible>
    </div>
  );
}
