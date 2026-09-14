export interface CourseItem {
  id: string;
  name: string;
  weight_percent: number;
  max_points: number;
  earned_points: number | null;
  due_date: string | null;
  status: "Not Started" | "In Progress" | "Done";
}

export interface CourseCategory {
  category_id: string;
  name: string;
  weight_percent: number;
  drop_lowest_n?: number;
  hurdle_min_percent?: number;
  hurdle_description?: string;
  items: CourseItem[];
}

export interface CourseHurdle {
  type: "category_average" | "all_completed" | "overall_minimum" | "custom";
  target_category?: string;
  min_percentage?: number;
  description: string;
}

export interface CourseData {
  course_code: string;
  course_name: string;
  credits: number;
  term: string;
  is_technical: boolean;
  grading_type: "percentage_gpa" | "sat_un";
  syllabus_file?: string;
  grade_scale: string;
  passing_criteria?: string[];
  categories: CourseCategory[];
  hurdles?: CourseHurdle[];
}

export interface CourseCalculation {
  course_code: string;
  completed_weight: number; // 0 to 100
  earned_weight: number;    // 0 to 100
  current_average: number | null; // 0 to 100
  projected_final: number; // 0 to 100
  letter_grade: string;
  gpa_points: number | null;
  hurdle_passed: boolean;
  hurdle_warnings: string[];
}

export interface SemesterCalculation {
  cumulative_gpa: number;
  projected_gpa: number;
  overall_current_average: number | null;
  technical_current_average: number | null;
  total_credits: number;
  completed_items_count: number;
  total_items_count: number;
}

/**
 * Converts percentage score to Seneca Polytechnic Official Letter Grade.
 * Scale:
 *   A+: 90% - 100% (GPA 4.0)
 *   A:  80% - 89%  (GPA 4.0)
 *   B+: 75% - 79%  (GPA 3.5)
 *   B:  70% - 74%  (GPA 3.0)
 *   C+: 65% - 69%  (GPA 2.5)
 *   C:  60% - 64%  (GPA 2.0)
 *   D+: 55% - 59%  (GPA 1.5)
 *   D:  50% - 54%  (GPA 1.0)
 *   F:  0% - 49%   (GPA 0.0)
 */
export function getSenecaLetterGrade(percent: number, isSatUn: boolean = false): string {
  if (isSatUn) {
    return percent >= 80 ? "SAT" : "UN";
  }
  if (percent >= 89.5) return "A+";
  if (percent >= 79.5) return "A";
  if (percent >= 74.5) return "B+";
  if (percent >= 69.5) return "B";
  if (percent >= 64.5) return "C+";
  if (percent >= 59.5) return "C";
  if (percent >= 54.5) return "D+";
  if (percent >= 49.5) return "D";
  return "F";
}

/**
 * Returns Seneca 4.0 GPA scale points for a letter grade.
 */
export function getSenecaGpaPoints(letter: string): number | null {
  switch (letter) {
    case "A+":
    case "A":
      return 4.0;
    case "B+":
      return 3.5;
    case "B":
      return 3.0;
    case "C+":
      return 2.5;
    case "C":
      return 2.0;
    case "D+":
      return 1.5;
    case "D":
      return 1.0;
    case "F":
      return 0.0;
    default:
      return null; // SAT/UN has no numerical GPA impact
  }
}

/**
 * Calculates grade progress, averages, and hurdle checks for a single course.
 */
export function calculateCourse(course: CourseData): CourseCalculation {
  let totalCompletedWeight = 0;
  let totalEarnedWeight = 0;
  const warnings: string[] = [];

  // Category-level breakdown for hurdle analysis
  const catStats: Record<string, { completedWeight: number; earnedWeight: number; totalItems: number; completedItems: number }> = {};

  for (const cat of course.categories) {
    catStats[cat.category_id] = { completedWeight: 0, earnedWeight: 0, totalItems: cat.items.length, completedItems: 0 };
    
    // Check for drop lowest score
    let items = [...cat.items];
    const dropN = cat.drop_lowest_n || 0;
    if (dropN > 0 && items.filter(i => i.earned_points !== null).length > dropN) {
      // Sort completed items by score percentage ascending
      const completed = items.filter(i => i.earned_points !== null)
        .sort((a, b) => ((a.earned_points! / a.max_points) - (b.earned_points! / b.max_points)));
      const droppedIds = new Set(completed.slice(0, dropN).map(i => i.id));
      items = items.filter(i => !droppedIds.has(i.id));
    }

    for (const item of items) {
      if (item.earned_points !== null && !isNaN(item.earned_points)) {
        const scoreFraction = Math.max(0, item.earned_points / item.max_points);
        const itemEarnedWeight = scoreFraction * item.weight_percent;
        
        totalCompletedWeight += item.weight_percent;
        totalEarnedWeight += itemEarnedWeight;

        catStats[cat.category_id].completedWeight += item.weight_percent;
        catStats[cat.category_id].earnedWeight += itemEarnedWeight;
        catStats[cat.category_id].completedItems += 1;
      }
    }
  }

  const currentAverage = totalCompletedWeight > 0 ? (totalEarnedWeight / totalCompletedWeight) * 100 : null;
  
  // Projected final: assume uncompleted deliverables earn current average (or 100% if nothing completed)
  const remainingWeight = Math.max(0, 100 - totalCompletedWeight);
  const baselineForRemaining = currentAverage !== null ? currentAverage : 100;
  const projectedFinal = Math.min(100, Math.max(0, totalEarnedWeight + (remainingWeight * (baselineForRemaining / 100))));

  const isSatUn = course.grading_type === "sat_un";
  const letterGrade = getSenecaLetterGrade(projectedFinal, isSatUn);
  const gpaPoints = getSenecaGpaPoints(letterGrade);

  // Check Hurdles
  let hurdlePassed = true;
  if (course.hurdles) {
    for (const h of course.hurdles) {
      if (h.type === "category_average" && h.target_category && catStats[h.target_category]) {
        const stat = catStats[h.target_category];
        if (stat.completedWeight > 0) {
          const catAvg = (stat.earnedWeight / stat.completedWeight) * 100;
          const minRequired = h.min_percentage ?? 50;
          if (catAvg < minRequired) {
            hurdlePassed = false;
            warnings.push(`Hurdle Alert: ${catAvg.toFixed(1)}% average in ${h.target_category} (Min ${minRequired}% required)`);
          }
        }
      } else if (h.type === "all_completed" && h.target_category && catStats[h.target_category]) {
        const stat = catStats[h.target_category];
        if (totalCompletedWeight >= 90 && stat.completedItems < stat.totalItems) {
          warnings.push(`Completion Hurdle: ${stat.completedItems}/${stat.totalItems} items completed in ${h.target_category}`);
        }
      }
    }
  }

  return {
    course_code: course.course_code,
    completed_weight: totalCompletedWeight,
    earned_weight: totalEarnedWeight,
    current_average: currentAverage,
    projected_final: projectedFinal,
    letter_grade: letterGrade,
    gpa_points: gpaPoints,
    hurdle_passed: hurdlePassed,
    hurdle_warnings: warnings
  };
}

/**
 * Calculates Semester-wide Cumulative GPA, Technical Average, and Progress.
 */
export function calculateSemester(courses: CourseData[]): SemesterCalculation {
  let gradedCredits = 0;
  let totalCredits = 0;
  let cumulativePointsSum = 0;
  let projectedPointsSum = 0;

  let overallWeightedAvgSum = 0;
  let overallCompletedCredits = 0;

  let techWeightedAvgSum = 0;
  let techCompletedCredits = 0;

  let totalItemsCount = 0;
  let completedItemsCount = 0;

  for (const c of courses) {
    totalCredits += c.credits;
    const calc = calculateCourse(c);

    // Count items
    for (const cat of c.categories) {
      for (const item of cat.items) {
        totalItemsCount++;
        if (item.earned_points !== null) completedItemsCount++;
      }
    }

    if (c.grading_type === "percentage_gpa") {
      gradedCredits += c.credits;

      if (calc.gpa_points !== null) {
        projectedPointsSum += calc.gpa_points * c.credits;
      }

      if (calc.current_average !== null) {
        // Use current letter grade for cumulative so far
        const currentLetter = getSenecaLetterGrade(calc.current_average, false);
        const currentGpa = getSenecaGpaPoints(currentLetter) ?? 0.0;
        cumulativePointsSum += currentGpa * c.credits;

        overallWeightedAvgSum += calc.current_average * c.credits;
        overallCompletedCredits += c.credits;

        if (c.is_technical) {
          techWeightedAvgSum += calc.current_average * c.credits;
          techCompletedCredits += c.credits;
        }
      }
    }
  }

  const cumulativeGpa = gradedCredits > 0 ? Number((cumulativePointsSum / gradedCredits).toFixed(2)) : 0.0;
  const projectedGpa = gradedCredits > 0 ? Number((projectedPointsSum / gradedCredits).toFixed(2)) : 0.0;
  const overallAvg = overallCompletedCredits > 0 ? Number((overallWeightedAvgSum / overallCompletedCredits).toFixed(1)) : null;
  const techAvg = techCompletedCredits > 0 ? Number((techWeightedAvgSum / techCompletedCredits).toFixed(1)) : null;

  return {
    cumulative_gpa: cumulativeGpa,
    projected_gpa: projectedGpa,
    overall_current_average: overallAvg,
    technical_current_average: techAvg,
    total_credits: totalCredits,
    completed_items_count: completedItemsCount,
    total_items_count: totalItemsCount
  };
}

/**
 * Calculates target grade requirements for What-If scenario analysis.
 */
export function calculateWhatIf(
  courseCalc: CourseCalculation,
  targetPercent: number
): { remainingWeight: number; requiredAvg: number; feasibility: "Secured" | "Achievable" | "Challenging" | "Impossible" | "Completed" } {
  const remainingWeight = Math.max(0, 100 - courseCalc.completed_weight);
  if (remainingWeight <= 0) {
    return {
      remainingWeight: 0,
      requiredAvg: 0,
      feasibility: "Completed"
    };
  }

  const pointsNeeded = targetPercent - courseCalc.earned_weight;
  const requiredAvg = (pointsNeeded / remainingWeight) * 100;

  let feasibility: "Secured" | "Achievable" | "Challenging" | "Impossible" | "Completed";
  if (requiredAvg <= 0) {
    feasibility = "Secured";
  } else if (requiredAvg > 100) {
    feasibility = "Impossible";
  } else if (requiredAvg >= 85) {
    feasibility = "Challenging";
  } else {
    feasibility = "Achievable";
  }

  return {
    remainingWeight,
    requiredAvg: Math.max(0, Number(requiredAvg.toFixed(1))),
    feasibility
  };
}
