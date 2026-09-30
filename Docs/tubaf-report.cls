\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{tubaf-report}[2024-04-18 TUBAF class for reports (based on scrreprt) by Max Weiner]

\DeclareKeys[tubaf-report]{}

\DeclareUnknownKeyHandler[tubaf-report]{%
    \PassOptionsToClass{\CurrentOption}{scrreprt}
}

\ProcessKeyOptions[tubaf-report]

\LoadClass[parskip=half]{scrreprt}

\RequirePackage{tubaf-logo}

\RequirePackage{tubaf-title}
\SetKeys[tubaf-title]{
    black=false,
    trapezoid=true
}

\RequirePackage{tubaf-marks}
\SetKeys[tubaf-marks]{
    footmark=author-title
}

\RequirePackage{tubaf-fonts}
