from fastmcp import FastMCP


def register(mcp: FastMCP):
    @mcp.prompt(tags={"image", "metadata", "privacy"})
    def audit_privacy(image_path: str, purpose: str = "publish on web") -> str:
        """Audit EXIF privacy risk for an intended use and recommend strip or keep."""
        return (
            f"Audit the privacy of {image_path} for intended use: {purpose}. "
            "Call get_image_properties, then get_exif_metadata. "
            "Look for sensitive fields: GPS, Make/Model, DateTimeOriginal, "
            "Artist, Copyright, SerialNumber. "
            "Cross-check with purpose: publish on web/social = high risk -> recommend strip_image_metadata; "
            "internal/client share = mask GPS but keep author/copyright; "
            "personal archive/legal evidence = keep everything. "
            "Return risk_level [high/medium/low], sensitive_fields[], "
            "recommendation [strip/keep/review], and why."
        )
