"""
Script to generate bell curve histogram statistics for all problems.
This creates/updates histogram data for TIME, STROKES, and CCPM data types.

Each histogram follows a bell curve (normal distribution) with all 25 bars filled.

Usage:
    python generate_histogram_stats.py
"""
import math
from typing import List
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models import Problem, ProblemHistogram, HistogramDataType


def normal_pdf(x: float, mean: float, std_dev: float) -> float:
    """
    Calculate the probability density function of a normal distribution.
    """
    variance = std_dev ** 2
    coefficient = 1 / math.sqrt(2 * math.pi * variance)
    exponent = -((x - mean) ** 2) / (2 * variance)
    return coefficient * math.exp(exponent)


def generate_bell_curve_counts(num_bins: int = 25, mean: float = 12.0, std_dev: float = 4.0, min_total: int = 500) -> List[float]:
    """
    Generate bell curve distribution counts for histogram bins.
    
    Args:
        num_bins: Number of bins (default 25)
        mean: Mean of the distribution (center of the curve, default 12.0 - middle of 25 bins)
        std_dev: Standard deviation (spread of the curve, default 4.0)
        min_total: Minimum total count across all bins (default 500 users)
    
    Returns:
        List of counts (floats) for each bin, ensuring all bins have at least 1 count
    """
    # Generate probabilities for each bin using normal distribution
    probabilities = []
    for bin_index in range(num_bins):
        prob = normal_pdf(float(bin_index), mean, std_dev)
        probabilities.append(prob)
    
    # Normalize probabilities so they sum to 1
    total_prob = sum(probabilities)
    normalized_probs = [p / total_prob for p in probabilities]
    
    # Scale to minimum total count, ensuring each bin gets at least 1
    # First, distribute the minimum across all bins
    base_counts = [1.0] * num_bins  # At least 1 count per bin
    remaining_count = max(0, min_total - num_bins)
    
    # Add remaining counts proportional to the bell curve distribution
    counts = []
    for i, prob in enumerate(normalized_probs):
        additional = prob * remaining_count
        counts.append(float(base_counts[i] + additional))
    
    return counts


def generate_histogram_stats_for_problem(db: Session, problem_id: int):
    """
    Generate bell curve histogram statistics for a single problem.
    Creates/updates histograms for TIME, STROKES, and CCPM.
    
    Note: Bin widths in backend are:
    - TIME: 2.5 seconds per bin
    - STROKES: 5.0 keystrokes per bin  
    - CCPM: 100.0 CCPM per bin
    """
    # Generate bell curve counts for all 25 bins
    # Mean around bin 12 (middle), std_dev 4.0 spreads it nicely
    bell_curve_counts = generate_bell_curve_counts(
        num_bins=25,
        mean=12.0,
        std_dev=4.0,
        min_total=600  # Total of ~600 users per histogram type
    )
    
    # Create/update histogram for each data type
    for data_type in HistogramDataType:
        # Check if histogram already exists
        histogram = db.query(ProblemHistogram).filter(
            ProblemHistogram.problem_id == problem_id,
            ProblemHistogram.data_type == data_type
        ).first()
        
        if histogram:
            # Update existing histogram
            histogram.values = bell_curve_counts
        else:
            # Create new histogram
            histogram = ProblemHistogram(
                problem_id=problem_id,
                data_type=data_type,
                values=bell_curve_counts
            )
            db.add(histogram)


def generate_all_histogram_stats():
    """
    Generate bell curve histogram statistics for all problems in the database.
    """
    db: Session = SessionLocal()
    
    try:
        # Get all problems
        problems = db.query(Problem).all()
        
        if not problems:
            print("No problems found in database. Please seed the database first.")
            return
        
        print(f"Found {len(problems)} problems. Generating histogram statistics...")
        
        # Generate histograms for each problem
        for problem in problems:
            generate_histogram_stats_for_problem(db, problem.id)
            print(f"  ✓ Generated histograms for problem {problem.id}: {problem.name}")
        
        # Commit all changes
        db.commit()
        print(f"\n✓ Successfully generated histogram statistics for {len(problems)} problems.")
        print("  Each problem now has bell curve distributions for TIME, STROKES, and CCPM.")
        print("  All 25 bins are filled with data following a normal distribution.")
        
    except Exception as e:
        db.rollback()
        print(f"Error generating histogram statistics: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    # Ensure tables are created
    print("Ensuring database tables exist...")
    Base.metadata.create_all(bind=engine)
    
    print("\nGenerating histogram statistics...\n")
    generate_all_histogram_stats()

