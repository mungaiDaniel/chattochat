import "./demoBanner.css";
import { DEMO_MODE } from "../../api";

export default function DemoBanner() {
  if (!DEMO_MODE) return null;
  return (
    <div className="demoBanner" role="status">
      Demo mode — sample data, changes are not saved.
    </div>
  );
}
