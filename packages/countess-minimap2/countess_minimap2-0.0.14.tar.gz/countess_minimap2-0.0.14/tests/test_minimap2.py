import pytest

import pandas as pd

from countess.core.logger import ConsoleLogger
from countess_minimap2 import MiniMap2Plugin

logger = ConsoleLogger()

df1 = pd.DataFrame([
        [ "CCAGAGAACTACGTGTCTGGGCCCAGCCCCCACCTGTGGGCAGAGCAGGGGAAGGGGACTTCCTCCGGGA" ],
        [ "CCAGAGAACTACGTGTCTGGGCCCAGCCCCCACCTGTGG" ],
        [ "CCAGAGAACTACGTGTCTGGGCCCAGCCCCCACCTGTGC" ],
        [ "CCAGAGAACTACGTGACTGGGCCCAGCCCCCACCTGTGG" ],
        [ "CGAGAGAACTACGTGTCTGGGCCCAGCCCCCACCTGTGG" ],
        [ "CCAGTGAACTACGTGTCTGGGCCCAGCCCCCACCTGTGG" ],
        [ "CCAGAGAACTACGTGTCTGGGCCCAGCCCCCACGTGTGG" ],
        [ "CCAGAGAACTACGTGTCTGGGCCCAGCCCCCACCTGTGGGCAGAGCAGGGGATGGGGACTTCCTCCGGGA" ],
        [ "CCAGAGAACTACGAGTCTGGGCCCAGCCCCCACCTGTGGGCAGAGCAGGGGAAGGGGACTTCCTCCGGGA" ],
        [ "CCAGAGAACTACGAGTCTGGGCCCAGCCCCCACCTGTGCGCAGAGCAGGGGAAGGGGACTTCCTCCGGGA" ],
    ],
    columns = ['sequence']
)

def test_1():
    plugin = MiniMap2Plugin()
    plugin.set_parameter("ref", "tests/irf4.fa")
    plugin.set_parameter("location", False)
    plugin.set_parameter("hgvs", True)

    plugin.prepare(["test"], None)
    dfo = plugin.process_dataframe(df1, logger)

    print(dfo)
