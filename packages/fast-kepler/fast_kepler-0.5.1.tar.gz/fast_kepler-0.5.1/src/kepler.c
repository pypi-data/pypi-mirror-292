#include <stdio.h>
#include <math.h>
#include <stdlib.h>

/*
Solution to Kepler's equation. Given mean anomaly, M, and eccentricity, e,
solve for E, the eccentric anomaly, which must satisfy:

    E - e sin(E) - M = 0

Follows the method of Danby 1988 as written in Murray and Dermot p36-37.
*/

// Helper function to calculate the sign of a number
static inline double sign(double x) {
    return (x >= 0) ? 1.0 : -1.0;
}

// Constants for Kepler solver
#define MAX_ITER 30
#define CONV_TOL 1.0e-12

double kepler(double M, double e) {
    double k = 0.85;  // Initial guess parameter
    double E = M + sign(sin(M)) * k * e; // First guess at E (eccentric anomaly)
    double fi = E - e * sin(E) - M;  // Initial value of the function fi
    int count = 0;

    while (fabs(fi) > CONV_TOL && count < MAX_ITER) {
        count++;
        
        // First, second, and third order derivatives of fi with respect to E
        double fip = 1 - e * cos(E); 
        double fipp = e * sin(E); 
        double fippp = -fipp;  // Use -fipp since it's equivalent to 1 - fip

        // First, second, and third order corrections to E
        double d1 = -fi / fip;
        d1 = -fi / (fip + d1 * fipp / 2.0); 
        d1 = -fi / (fip + d1 * fipp / 2.0 + d1 * d1 * fippp / 6.0);
        
        E += d1;
        fi = E - e * sin(E) - M;  // Recalculate fi with the updated E
        
        // Check for non-convergence
        if (count == MAX_ITER) {
            fprintf(stderr, "Error: kepler not converging after %d iterations.\n", MAX_ITER);
            fprintf(stderr, "E = %f, M = %f, e = %f\n", E, M, e);
            return -1;  // Indicate an error condition
        }
    }

    return E;  // Return the eccentric anomaly
}

#define PI 3.141592653589793

// Function to calculate radial velocity
double calc_c_rv0(double t, double per, double k, double phase, double e, double cosom, double sinom) {
    // Compute mean anomaly (M) and frequency (freq)
    double freq = 2 * PI / per;
    double M = fmod(freq * t + phase, 2 * PI);  // Mean anomaly

    // Calculate eccentric anomaly (E) using the Kepler solver
    double E = kepler(M, e);

    // Calculate the ratio related to the eccentric anomaly (tan(E/2))
    double ratio = sqrt((1 + e) / (1 - e)) * tan(E / 2);

    // Calculate the factor for radial velocity
    double fac = 2 / (1 + ratio * ratio);

    // Calculate the radial velocity
    double rv = k * (cosom * (fac - 1) - ratio * fac * sinom + e * cosom);

    return rv;
}


// Function to calculate radial velocity using time of periastron passage (tp)
double calc_c_rv1(double t, double per, double k, double tp, double e, double cosom, double sinom) {
    // Calculate phase based on time and time of periastron (tp)
    double phase = (t - tp) / per;

    // Calculate mean anomaly (M) by removing the integer part of phase
    double M = 2 * PI * (phase - floor(phase));

    // Calculate eccentric anomaly (E) using the Kepler solver
    double E = kepler(M, e);

    // Calculate the ratio related to eccentric anomaly (tan(E/2))
    double ratio = sqrt((1 + e) / (1 - e)) * tan(E / 2);

    // Calculate the factor for radial velocity
    double fac = 2 / (1 + ratio * ratio);

    // Calculate the radial velocity
    double rv = k * (cosom * (fac - 1) - ratio * fac * sinom + e * cosom);

    return rv;
}


// Test function for the kepler function
int main() {
    double M, e, E;

    // Prompt user for input and check input validity
    printf("Enter M (mean anomaly, in radians): ");
    if (scanf("%lf", &M) != 1) {
        printf("Error: Invalid input for M.\n");
        return 1;  // Return error code
    }

    printf("Enter e (eccentricity, 0 <= e < 1): ");
    if (scanf("%lf", &e) != 1 || e < 0 || e >= 1) {
        printf("Error: Invalid input for e. Eccentricity must be in range [0, 1).\n");
        return 1;  // Return error code
    }

    // Solve for eccentric anomaly using the kepler function
    E = kepler(M, e);

    // Output the result with high precision
    printf("The eccentric anomaly E is: %.12lf\n", E);

    return 0;  // Successful exit
}