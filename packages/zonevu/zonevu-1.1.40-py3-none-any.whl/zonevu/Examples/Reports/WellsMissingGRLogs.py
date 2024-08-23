#  Copyright (c) 2024 Ubiterra Corporation. All rights reserved.
#  #
#  This ZoneVu Python SDK software is the property of Ubiterra Corporation.
#  You shall use it only in accordance with the terms of the ZoneVu Service Agreement.
#  #
#  This software is made available on PyPI for download and use. However, it is NOT open source.
#  Unauthorized copying, modification, or distribution of this software is strictly prohibited.
#  #
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
#  INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
#  PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
#  FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#  ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
#

from ...Zonevu import Zonevu
from typing import List
from ...DataModels.Wells.Well import WellEntry
from ...Services.WellService import WellData
from ...DataModels.Wells.Curve import AppMnemonicCodeEnum
from typing import Optional
from tabulate import tabulate


def main(zonevu: Zonevu, output_path) -> None:
    print('List all wells in ZoneVu account that do not have a GR well log curve')
    well_svc = zonevu.well_service
    well_entries = well_svc.find_by_name()
    print('Number of wells retrieved = %s' % len(well_entries))
    print()
    # Figure out which of these wells do not have a well log with at least one gamma ray curve
    headers = ["Well Name", "Has Logs", "Has Gamma"]
    print()
    print()
    rows: List[List[str]] = []
    for well_entry in well_entries:
        well = well_svc.find_by_id(well_entry.id)
        well_svc.load_well(well, {WellData.logs})
        well_bore = well.primary_wellbore
        curves = well_bore.well_log_curves
        has_curves = len(curves) > 0
        has_gamma = any(curve.system_mnemonic == AppMnemonicCodeEnum.GR for curve in curves)
        row = [well.full_name, str(has_curves), str(has_gamma)]
        rows.append(row)

    print(tabulate(rows, headers, tablefmt="tsv"))



