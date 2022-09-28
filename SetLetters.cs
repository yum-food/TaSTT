using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

// Expands a list of 4-byte parameters into a longer list of (effectively)
// 1-byte parameters. The 1-byte parameters are easier to use in an animation
// layer, since we can write conditions for them.
[SharedBetweenAnimators]
public class SetLetters : StateMachineBehaviour
{
  Dictionary<string, int> letters_;
  List<string> cell_parameters_;
  List<string> group_parameters_;

  int GetLetterFromGroup(int g, int which)
  {
    return (((g & (0x000000FF << (which * 8))) >> (which * 8)) & 0x000000FF);
  }

  // This function is called in 2 contexts:
  // 1. animator.parameters contains everything we need. Updating params is not
  //    reflected in emulator.
  // 2. animator.parameters contains nothing we need. Updating params is
  //    reflected in emulator.
  override public void OnStateUpdate(Animator animator, AnimatorStateInfo stateInfo, int layerIndex)
  {
    if (letters_ == null) {
      letters_ = new Dictionary<string, int>();
    }

    // I don't know why or how but Unity fucking refuses to save this variable,
    // so reinitialize it every time, YOLO.
    cell_parameters_ = new List<string> {
      "_Letter_Row00_Col00",
        "_Letter_Row00_Col01",
        "_Letter_Row00_Col02",
        "_Letter_Row00_Col03",
        "_Letter_Row00_Col04",
        "_Letter_Row00_Col05",
        "_Letter_Row00_Col06",
        "_Letter_Row00_Col07",
        "_Letter_Row00_Col08",
        "_Letter_Row00_Col09",
        "_Letter_Row00_Col10",
        "_Letter_Row00_Col11",
        "_Letter_Row00_Col12",
        "_Letter_Row00_Col13",
        "_Letter_Row01_Col00",
        "_Letter_Row01_Col01",
        "_Letter_Row01_Col02",
        "_Letter_Row01_Col03",
        "_Letter_Row01_Col04",
        "_Letter_Row01_Col05",
        "_Letter_Row01_Col06",
        "_Letter_Row01_Col07",
        "_Letter_Row01_Col08",
        "_Letter_Row01_Col09",
        "_Letter_Row01_Col10",
        "_Letter_Row01_Col11",
        "_Letter_Row01_Col12",
        "_Letter_Row01_Col13",
        "_Letter_Row02_Col00",
        "_Letter_Row02_Col01",
        "_Letter_Row02_Col02",
        "_Letter_Row02_Col03",
        "_Letter_Row02_Col04",
        "_Letter_Row02_Col05",
        "_Letter_Row02_Col06",
        "_Letter_Row02_Col07",
        "_Letter_Row02_Col08",
        "_Letter_Row02_Col09",
        "_Letter_Row02_Col10",
        "_Letter_Row02_Col11",
        "_Letter_Row02_Col12",
        "_Letter_Row02_Col13",
    };
    group_parameters_ = new List<string> {
      "_Letter_Row00_Col00_03",
        "_Letter_Row00_Col04_07",
        "_Letter_Row00_Col08_11",
        "_Letter_Row00_Col12_13",
        "_Letter_Row01_Col00_03",
        "_Letter_Row01_Col04_07",
        "_Letter_Row01_Col08_11",
        "_Letter_Row01_Col12_13",
        "_Letter_Row02_Col00_03",
        "_Letter_Row02_Col04_07",
        "_Letter_Row02_Col08_11",
        "_Letter_Row02_Col12_13",
    };

    bool got_match = false;
    foreach (var param in animator.parameters) {
      if (param.name == "_Letter_Row00_Col00_03") {
        got_match = true;
        break;
      }
    }
    if (!got_match) {
      if (!letters_.ContainsKey(cell_parameters_[0])) {
        return;
      }
      foreach (var param in cell_parameters_) {
        animator.SetInteger(param, letters_[param]);
      }
      
      return;
    }

    int cell_idx = 0;
    for (int i = 0; i < group_parameters_.Count; i++) {
      string group_param = group_parameters_[i];
      int g = animator.GetInteger(group_param);

      string cell_param = cell_parameters_[cell_idx];
      letters_[cell_param] = GetLetterFromGroup(g, 0);
      cell_idx += 1;

      cell_param = cell_parameters_[cell_idx];
      letters_[cell_param] = GetLetterFromGroup(g, 1);
      cell_idx += 1;

      // If we're on the last group of 4 in a row, we do not look at the cells,
      // since there are only 14 cells in each row.
      if (i % 4 != 3) {
        cell_param = cell_parameters_[cell_idx];
        letters_[cell_param] = GetLetterFromGroup(g, 2);
        cell_idx += 1;

        cell_param = cell_parameters_[cell_idx];
        letters_[cell_param] = GetLetterFromGroup(g, 3);
        cell_idx += 1;
      }
    }
  }
}
