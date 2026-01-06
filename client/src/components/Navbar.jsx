import { Link, useLocation } from "react-router-dom";
import "../styles/Navbar.css";

function Navbar() {
    const location = useLocation();

    return (
        <nav className="navbar">
            <div className="navbar-brand">StockSense</div>
            <div className="navbar-links">
                <Link to="/" className={location.pathname === "/" ? "active" : ""}>
                    Research
                </Link>
                <Link to="/articles" className={location.pathname === "/articles" ? "active" : ""}>
                    Articles
                </Link>
            </div>
            <div className="navbar-spacer"></div> 
        </nav>
    );
}

export default Navbar;