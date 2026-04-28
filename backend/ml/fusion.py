from datetime import datetime
import uuid

class ThreatFusionEngine:
    WEIGHTS = {"network": 0.30, "log": 0.20, "phishing": 0.25, "malware": 0.25}
    SEVERITY = [
        (0.3, "LOW", "#22c55e"),
        (0.6, "MEDIUM", "#eab308"),
        (0.8, "HIGH", "#f97316"),
        (1.0, "CRITICAL", "#ef4444")
    ]

    def fuse(self, module_results: dict) -> dict:
        total_weight = 0.0
        weighted_sum = 0.0
        
        recs = []
        scores_map = {}
        
        for mod, result in module_results.items():
            if "error" in result:
                continue
                
            score = result.get("threat_score", 0.0)
            weight = self.WEIGHTS.get(mod, 0.0)
            
            weighted_sum += score * weight
            total_weight += weight
            scores_map[mod] = score
            
            if score > 0.6:
                if mod == "network":
                    recs.append("Isolate affected IPs at the firewall level.")
                    recs.append("Inspect concurrent lateral movement packets.")
                elif mod == "log":
                    recs.append("Review authentication services (SSHD) for brute force logic.")
                    recs.append("Monitor kernel panics causing system instability.")
                elif mod == "phishing":
                    recs.append("Block evaluated domains in enterprise DNS configs.")
                elif mod == "malware":
                    recs.append("Quarantine the uploaded asset. Trigger EDR full sweep.")
            
        if total_weight > 0:
            final_score = weighted_sum / total_weight
        else:
            final_score = 0.0
            
        sev_label, sev_color = self.SEVERITY[0][1], self.SEVERITY[0][2]
        for limit, label, color in self.SEVERITY:
            if final_score <= limit:
                sev_label = label
                sev_color = color
                break
                
        if not recs:
            recs.append("No immediate action required. Continue baseline monitoring.")
            
        return {
            "final_threat_score": float(final_score),
            "severity": sev_label,
            "severity_color": sev_color,
            "module_scores": scores_map,
            "recommendations": recs,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "session_id": str(uuid.uuid4())
        }

fusion_engine = ThreatFusionEngine()
