MODULE es

CONTAINS

  SUBROUTINE excursion_set_fftw(photon_field, Mhyd_field, qi, plan_bwd, plan_fwd, kmag, HIfilter)
    IMPLICIT NONE

    REAL, DIMENSION(:,:,:), INTENT(in) :: photon_field, Mhyd_field
    REAL, DIMENSION(SIZE(photon_field, 1), SIZE(photon_field, 2), SIZE(photon_field, 3)), INTENT(out) :: qi
    INTEGER*8, INTENT(inout) :: plan_bwd, plan_fwd
    REAL, DIMENSION(:,:,:), INTENT(in) :: kmag
    INTEGER, intent(in) :: HIfilter

    INTEGER :: i, j, k, ii, ngrid, ncorr
    DOUBLE COMPLEX, DIMENSION(:,:,:), ALLOCATABLE :: field, photon_k, Mhyd_k
    REAL, DIMENSION(:,:,:), ALLOCATABLE :: photon_filtered, Mhyd_filtered

    REAL :: dlogr, rmin, rmax
    REAL, DIMENSION(:), ALLOCATABLE :: r, rhi, rlo

    REAL, parameter :: pi = 3.1415927
    REAL, PARAMETER :: two_pi = 2.0 * 3.1415927


    ngrid = SIZE(Mhyd_field, dim=1)
    qi(:,:,:) = 0.0
    WHERE (Mhyd_field > 0.0) qi = MIN(1.0, photon_field / Mhyd_field)
    !PRINT *,'x_min',SUM(DBLE(qi))/REAL(ngrid*ngrid*ngrid)

    ALLOCATE(field(ngrid,ngrid,ngrid), photon_k(ngrid,ngrid,ngrid), Mhyd_k(ngrid,ngrid,ngrid), photon_filtered(ngrid,ngrid,ngrid), Mhyd_filtered(ngrid,ngrid,ngrid))

    ! Inverse FFT of the photon field
    field = CMPLX(DBLE(photon_field), 0.d0, kind=8)
    CALL order_frequencies(field)
    CALL dfftw_execute_dft(plan_bwd, field, field)
    photon_k = field

    ! Inverse FFT of the non-linear density
    field = CMPLX(DBLE(Mhyd_field), 0.d0, kind=8)
    CALL order_frequencies(field)
    CALL dfftw_execute_dft(plan_bwd, field, field)
    Mhyd_k = field

    ! Set the length scales for filtering (assuming box = 1)
    rmax = 0.5
    rmin = 1.0 / REAL(ngrid) * (3.0 / (4.0 * pi)) ** (1./3.)
    dlogr=0.1 * 0.434
    ncorr=INT((LOG10(rmax) - LOG10(rmin)) / dlogr + 1.5) + 1
    ALLOCATE(r(ncorr), rhi(ncorr), rlo(ncorr))
    DO ii = 1, ncorr
       r(ii) = 10.0 ** (LOG10(rmin) + (ii-1) * dlogr)
       rlo(ii) = r(ii) * 10.0 ** (-0.5 * dlogr)
       rhi(ii) = r(ii) * 10.0 ** (0.5 * dlogr)
    END DO
    !PRINT *,'rmax, rmin',rmax,rmin


    ! Loop over length scales starting with the largest
    DO ii=ncorr, 1, -1
       !PRINT *,ii
       !$OMP PARALLEL DO DEFAULT(SHARED) PRIVATE (k,j,i,kmag)
       DO k = 1, ngrid
          DO j = 1, ngrid
             DO i = 1, ngrid
                IF (HIfilter == 0) THEN
                   field(i,j,k) = photon_k(i,j,k) * filter_sth(kmag(i,j,k) * r(ii))
                ELSEIF (HIfilter == 1) THEN
                   field(i,j,k) = photon_k(i,j,k) * filter_sharpk(kmag(i,j,k) * r(ii))
                END IF
             END DO
          END DO
       END DO
       CALL dfftw_execute_dft(plan_fwd, field, field)
       CALL order_frequencies(field)
       field = field / REAL(ngrid) ** 3
       photon_filtered = REAL( SIGN(ABS(field), REAL(field)) )

       !$OMP PARALLEL DO DEFAULT(SHARED) PRIVATE (k,j,i,kmag)
       DO k = 1, ngrid
          DO j = 1, ngrid
             DO i = 1, ngrid
                IF (HIfilter == 0) THEN
                   field(i,j,k) = Mhyd_k(i,j,k) * filter_sth(kmag(i,j,k) * r(ii))
                ELSEIF (HIfilter == 1) THEN
                   field(i,j,k) = Mhyd_k(i,j,k) * filter_sharpk(kmag(i,j,k) * r(ii))
                END IF
             END DO
          END DO
       END DO
       CALL dfftw_execute_dft(plan_fwd, field, field)
       CALL order_frequencies(field)
       field = field / REAL(ngrid) ** 3
       Mhyd_filtered = REAL( SIGN(ABS(field), REAL(field)) )
       !PRINT *,MINVAL(Mhyd_filtered), MINVAL(Mhalo_filtered)

       !$OMP PARALLEL DO DEFAULT(SHARED) PRIVATE (k,j,i) !! reduction(+:numion)
       DO k = 1, ngrid
          DO j = 1, ngrid
             pointsloop: DO i = 1, ngrid
                IF (qi(i,j,k) < 1.0) THEN
                   photon_filtered(i,j,k) = MAX(0.0, photon_filtered(i,j,k))
                   Mhyd_filtered(i,j,k) = MAX(0.0, Mhyd_filtered(i,j,k))
                   IF (photon_filtered(i,j,k) > 0.0 .AND. photon_filtered(i,j,k) > Mhyd_filtered(i,j,k)) qi(i,j,k) = 1.0
                END IF
             END DO pointsloop
          END DO
       END DO
    END DO

  END SUBROUTINE excursion_set_fftw


  SUBROUTINE order_frequencies(array)
    ! Order frequencies before/after FFT
    IMPLICIT NONE
    DOUBLE COMPLEX, DIMENSION(:,:,:), INTENT(inout) :: array
    INTEGER :: i,j,k,n

    n=SIZE(array,dim=1)
    !$OMP PARALLEL DO DEFAULT(SHARED) PRIVATE (i,j,k)
    DO k=1,n
       DO j=1,n
          DO i=1,n
             array(i,j,k)=array(i,j,k)*(-1.)**(i+j+k-3)
          END DO
       END DO
    END DO

  END SUBROUTINE order_frequencies


!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


  FUNCTION filter_gauss(x)
    IMPLICIT NONE
    REAL :: x,filter_gauss

    filter_gauss=EXP(-x*x)
  END FUNCTION filter_gauss

  FUNCTION filter_sharpk(x)
    IMPLICIT NONE
    REAL :: x,filter_sharpk


    IF (ABS(x) <= 1.0) THEN
       filter_sharpk=1.0
    ELSE
       filter_sharpk=0.0
    END IF
  END FUNCTION filter_sharpk

  FUNCTION filter_sth(x)
    IMPLICIT NONE
    REAL :: x,filter_sth

    IF (ABS(x) < 1.e-8) THEN
       filter_sth=1.0
    ELSE
       filter_sth=3.0*(SIN(x)-x*COS(x))/x**3
    END IF

  END FUNCTION filter_sth

  FUNCTION filter_1D(x)
    IMPLICIT NONE
    REAL :: x,filter_1D

    IF (ABS(x) < 1.e-8) THEN
       filter_1D=1.0
    ELSE
       filter_1D=SIN(x)/x
    END IF
  END FUNCTION filter_1D


!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!




END MODULE es
