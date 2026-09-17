import "./Hero3D.css";
import { asset } from "../../api";

export default function Hero3D({ profile }) {
  return (
    <div className="hero3d">
      <div className="hero3d-grid" />

      <div className="hero3d-photo-wrap">
        {profile?.photo_url ? (
          <img
            src={asset(profile.photo_url)}
            alt="Subham Das"
            className="hero3d-photo"
          />
        ) : (
          <div className="hero3d-placeholder">
            <span>AI</span>
          </div>
        )}

        <div className="hero3d-ring ring-1" />
        <div className="hero3d-ring ring-2" />
        <div className="hero3d-ring ring-3" />
      </div>

      {/* <div className="float f1">&lt;ML /&gt;</div> */}
      <div className="float f1">AI • ML</div>

      <div className="float f2">
        Learn
        <br />
        Build
        <br />
        Improve
      </div>

      <div className="hero3d-label">NEURAL WORKSPACE</div>
    </div>
  );
}