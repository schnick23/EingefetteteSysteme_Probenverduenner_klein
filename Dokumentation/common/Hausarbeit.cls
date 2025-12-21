% Hausarbeit.cls – Minimal-Layout für Dokumente
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{common/Hausarbeit}[2025/08/12 v1.1 Minimal-Layout]

% Alle unbekannten Optionen an article weiterreichen (z.B. 12pt, twocolumn, etc.)
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions\relax

% Basis-Klasse
\LoadClass[12pt]{article}

% Schriften, Sprache, Mikrotypografie
\RequirePackage[utf8]{inputenc} % nur bei pdfLaTeX
\RequirePackage[T1]{fontenc}
\RequirePackage[ngerman]{babel} % deutsche & englische Texte

% Arial-ähnliche Schrift (über Paket helvet)
%\RequirePackage[scaled]{helvet} % Helvetica (Arial-ähnlich)
%\renewcommand{\familydefault}{\sfdefault} % Standard auf Sans Serif setzen

% Times New Roman (über Paket newtxtext und newtxmath)
\RequirePackage{newtxtext,newtxmath} % Times-Schriften für Text und Mathematik
\renewcommand{\familydefault}{\rmdefault} % Serifenschrift als Standard

\RequirePackage{microtype} % bessere Silbentrennung & Zeichenabstände

% Seitenlayout
\usepackage[a4paper,top=2cm,bottom=2cm,left=2cm,right=2cm,includefoot]{geometry}
\setlength{\parindent}{0pt}
\RequirePackage{ragged2e}

% Zeilenabstand
\RequirePackage{setspace}
\setstretch{1.25}

% Mathematik
\let\Bbbk\relax
\let\openbox\relax
\RequirePackage{amsmath,amssymb,amsthm} % Mathe-Umgebungen & Symbole
\RequirePackage{siunitx} % Einheiten wie \SI{10}{\meter\per\second}
\RequirePackage{mathtools} % Erweiterung zu amsmath

% Bilder, Tabellen
\RequirePackage{graphicx} % Bilder einfügen
\RequirePackage{float} % genaues Platzieren mit [H]
\RequirePackage{booktabs} % schönere Tabellen
\RequirePackage{tabularx} % Tabellen mit automatischer Spaltenbreite
\RequirePackage{array} % erweiterte Tabellenspalten-Optionen
\RequirePackage{longtable} % Tabellen über mehrere Seiten
\RequirePackage{xcolor} % Farben
\RequirePackage[table]{xcolor} % wichtig: [table]!
\RequirePackage{colortbl}      % (optional) für stabilere Tabellenfärbung
\RequirePackage{caption}      % (optional) für erweiterte Bild-/Tabellenbeschriftungen
\RequirePackage{subcaption}   % (optional) für Unterabbildungen/-tabellen
\RequirePackage{makecell}    % (optional) für Zeilenumbrüche in Tabellenköpfen

% Quellenverzeichnis
% \RequirePackage[
%   backend=biber,
%   style=ieee, % oder numeric, apa, ieee
%   sorting=nyt
% ]{biblatex}
% \DeclareLanguageMapping{ngerman}{ngerman-apa}
% Beispiel: \addbibresource{literatur.bib}

% Sonstiges
\newcommand{\TODO}[1]{\textcolor{red}{\textbf{#1}}}
\RequirePackage{comment} % um große Textblöcke auszukommentieren
\RequirePackage{csquotes} % korrekte Anführungszeichen abhängig von Sprache
\RequirePackage{hyperref} % klickbare Links, PDF-Metadaten
\hypersetup{colorlinks=true, linkcolor=gray, citecolor=red, urlcolor=blue}

\RequirePackage{pgffor} % für \foreach

% Code
\RequirePackage{listings}
\RequirePackage{lstautogobble}
\RequirePackage{courier}
\RequirePackage{listings}
\RequirePackage{xcolor}
\RequirePackage{inconsolata} % hübsche Mono-Schrift

\lstset{
    language=C,          % Programmiersprache
    basicstyle=\small\ttfamily,  % Standardschrift
    numbers=left,           % Zeilennummern links
    numberstyle=\tiny\color{gray},
    stepnumber=5,           % jede 5. Zeile nummerieren
    numbersep=8pt,        % Abstand der Nummern zum Text
    backgroundcolor=\color{white}, % Hintergrundfarbe
    keywordstyle=\color{blue}\bfseries,
    commentstyle=\color{green!50!black}\itshape,
    morecomment=[l]{\#}, % Kommentare beginnen mit #
    morecomment=[l]{--}, % Kommentare beginnen mit --
    stringstyle=\color{orange!90!black},
    breaklines=true,        % Zeilen automatisch umbrechen
    frame=lines,           % Rahmen
    tabsize=4,
    showstringspaces=false,
    captionpos=b           % Caption unten
}


% Kopf- und Fußzeile
\RequirePackage{fancyhdr}
\RequirePackage{lastpage}
\pagestyle{fancy}
\fancyhf{}
\RequirePackage{titlesec} % um Überschriftenformat anzupassen

% ---- fancyhdr Grundsetup (einmal in der Klasse)
\RequirePackage{fancyhdr}
\setlength{\headheight}{ 36pt }
\setlength{\headsep}{20pt}
\newcommand{\headerlogo}{images/Nordakademie_Logo.png}
\renewcommand{\headrule}{\vspace{4pt}\hrule}

% Abschnittstitel in die Kopfzeile (ohne Nummer)
\RequirePackage{titlesec}
\renewcommand{\sectionmark}[1]{\markright{#1}}
\renewcommand{\subsectionmark}[1]{}

% Eigene Seitenstile definieren (NAMED styles)
\fancypagestyle{transferfancy}{%
  \fancyhf{}%
  \fancyhead[L]{\nouppercase{\rightmark}}%
  \fancyhead[R]{\includegraphics[height=0.8cm]{\headerlogo}}%
  \fancyfoot[R]{\thepage}%
  \renewcommand{\headrulewidth}{0.4pt}%
  \renewcommand{\footrulewidth}{0pt}%
}
\fancypagestyle{transferplain}{%
  \fancyhf{}%
  \fancyhead[L]{}% links leer
  \fancyhead[R]{\includegraphics[height=0.8cm]{\headerlogo}}%
  \fancyfoot[R]{\thepage}%
  \renewcommand{\headrulewidth}{0.4pt}%
  \renewcommand{\footrulewidth}{0pt}%
}

% ---- Umschalt-Befehle (so kannst du sie direkt im Dokument nutzen)
\newcommand{\frontmatterformat}{%
  \clearpage
  \setcounter{secnumdepth}{0} % Keine Numerierung von Überschriften
  \pagenumbering{Roman}%
  \setcounter{page}{2}% <-- Start bei II
  \pagestyle{transferplain}%
}

\newcommand{\mainmatterformat}{%
  \clearpage
  \setcounter{secnumdepth}{3} % Überschriften wieder numerieren
  \pagenumbering{arabic}%
  \pagestyle{transferfancy}%
}

\newcommand{\backmatterformat}{%
  \clearpage
  \setcounter{secnumdepth}{0} % Keine Numerierung von Überschriften
  \pagenumbering{Roman}%
  \pagestyle{transferplain}%
}



% genug Platz für die Kopfzeile
\setlength{\headheight}{ 36pt }
\setlength{\headsep}{18pt}


% ----- Abbildungs- und Tabellenverzeichnis (automatisch mit TOC-Eintrag)
\newcommand{\printfiguresintoc}{%
  \begingroup
    \phantomsection
    \renewcommand{\listfigurename}{Abbildungsverzeichnis}%
    \addcontentsline{toc}{section}{\listfigurename}%
    \listoffigures
  \endgroup
  \clearpage
}

\newcommand{\printtablesintoc}{%
  \begingroup
    \phantomsection
    \renewcommand{\listtablename}{Tabellenverzeichnis}%
    \addcontentsline{toc}{section}{\listtablename}%
    \listoftables
  \endgroup
  \clearpage
}

% ----- Abkürzungsverzeichnis (acronym)
\RequirePackage{acronym}


\addto\extrasngerman{%
    \renewcommand{\sectionautorefname}{Kapitel}%
    \renewcommand{\subsectionautorefname}{Kapitel}%
    \renewcommand{\subsubsectionautorefname}{Kapitel}%
}



\RequirePackage{wrapfig} % Bilder mit Textumfluss
 



