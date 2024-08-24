import re

regex = r"""\n
    (?=^\*+ # bold / italics at the start
        (
            (Where?fore)|
            (WHERE?FORE)|
            (WHEREFORE,\s+PREMISES\s+CONSIDERED)| # 65020
            (ACCORDINGLY)| # ACCORDINGLY examples, SOURCE.geturl()/1/63290; SOURCE.geturl()/1/64934
            (IN\s+
                (VIEW|LIGHT)\s+ # IN VIEW WHEREOF SOURCE.geturl()/1/33483; IN LIGHT OF ALL THE FOREGOING (46135)
                (
                    (W?HEREOF)| # IN VIEW HEREOF SOURCE.geturl()/1/33471
                    (THEREOF)| # IN VIEW THEREOF SOURCE.geturl()/1/34340
                    (
                        OF\s+
                        (ALL\s+)?
                        THE\s+
                        FOREGOING
                        (
                            \s+PREMISES|
                            \s+DISQUISITIONS?
                        )?
                    )| # IN VIEW OF ALL THE FOREGOING SOURCE.geturl()/1/64489
                    (OF\s+THESE\s+CONSIDERATIONS) # SOURCE.geturl()/1/33679
                )
            )|
            (
                (GIVEN\s+)?
                THE\s+FOREGOING\s+
                (
                    DISCOURSE|
                    PREMISES?|
                    DISQUISITIONS?
                )
                (\s+CONSIDERED)?
            )|
            (ON\s+ALL\s+THE\s+FOREGOING\s+CONSIDERATIONS)| # SOURCE.geturl()/1/33964
            (CONSIDERING\s+THE\s+FOREGOING)| # SOURCE.geturl()/1/33587, SOURCE.geturl()/1/34150, SOURCE.geturl()/1/34759
            (PREMISES CONSIDERED)| # SOURCE.geturl()/1/33729
            (FOR\s+
                (
                    THE\s+FOREGOING|
                    THESE|
                    THE\s+STATED
                )
                \s+
                REASONS
            )| # SOURCE.geturl()/1/33600
            (UPON\s+THESE\s+PREMISES) # SOURCE.geturl()/1/34578
        )
        \,?
        \*+
        .*?
    )"""  # noqa: E501

pattern = re.compile(regex, re.X | re.M)


def add_fallo_comment(text: str):
    """Adds an html comment to mark the portion of a decision as being
    part of the judgment."""
    if not re.search(r"(<!--\s*##\s+Fallo\s*-->)", text):
        if len(pattern.findall(text)) == 1:
            return pattern.sub("\n\n<!-- ## Fallo -->\n", text)
    return text
