MODULE rsd

CONTAINS

  SUBROUTINE rsd_grid(box_los, z_los, omega_m, omega_l, in_field, velocity_los, out_field, nsubgrid, periodic)
    IMPLICIT NONE

    REAL, INTENT(in) :: box_los, omega_m, omega_l
    REAL, DIMENSION(:), INTENT(in) :: z_los
    REAL, DIMENSION(:,:,:), INTENT(in) :: in_field, velocity_los
    REAL, DIMENSION(:,:,:), INTENT(out) :: out_field
    INTEGER, INTENT(in) :: nsubgrid
    LOGICAL, INTENT(in) :: periodic

    INTEGER :: i,j,k, isubgrid, k_subgrid, k_new
    INTEGER :: klo, khi
    INTEGER :: ngrid_x, ngrid_y, ngrid_los

    REAL :: dx, dx_subgrid, x_subgrid, wt_lo, wt_hi
    REAL :: field_subgrid, vlos_subgrid, delta_x, x_new, E_Hubble


    ngrid_x = SIZE(in_field, dim=1)
    ngrid_y = SIZE(in_field, dim=2)
    ngrid_los = SIZE(in_field, dim=3) !! the size can be different along the los

    dx = box_los / REAL(ngrid_los)
    dx_subgrid = dx / REAL(nsubgrid)

    out_field = 0.0

    DO i = 1, ngrid_x
       DO j = 1, ngrid_y

          losloop: DO k = 1, ngrid_los
             klo = k
             khi = k + 1
             E_Hubble = REAL( SQRT((1.0 - omega_m - omega_l) * (1.0 + z_los(k)) ** 2 + omega_m * (1.0 + z_los(k)) ** 3 + omega_l) )!!! ignore omega_r

             IF (khi > ngrid_los) THEN
                IF (periodic) THEN
                   khi = khi - ngrid_los
                ELSE
                   CYCLE losloop  !!! if not periodic, then the boundary points may not be correctly computed
                END IF
             END IF
             subgridloop: DO isubgrid = 1, nsubgrid
                x_subgrid = (k - 1) * dx + (isubgrid - 1) * dx_subgrid
                k_subgrid = MODULO(NINT(x_subgrid / dx), ngrid_los) + 1

                wt_lo = 1.0 - ((isubgrid - 1) * dx_subgrid) / dx
                wt_hi = 1.0 - wt_lo

                field_subgrid = in_field(i,j, k_subgrid) / REAL(nsubgrid)
                vlos_subgrid = wt_lo * velocity_los(i,j,klo) + wt_hi * velocity_los(i,j,khi)

                delta_x = vlos_subgrid * (1 + z_los(k)) / (100.0 * E_Hubble)
                x_new = x_subgrid + delta_x
                IF (periodic) THEN
                   k_new = MODULO(NINT(x_new / dx), ngrid_los) + 1
                ELSE
                   k_new = NINT(x_new / dx) + 1
                   IF (k_new > ngrid_los) CYCLE subgridloop
                END IF

                out_field(i,j, k_new) = out_field(i,j, k_new) + field_subgrid
             END DO subgridloop
          END DO losloop

       END DO
    END DO


  END SUBROUTINE rsd_grid
END MODULE rsd
