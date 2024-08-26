MODULE fcoll_grid

  DOUBLE PRECISION, PARAMETER :: pi=3.14159265358979324d0
  DOUBLE PRECISION, PARAMETER :: two_pi=2.d0*pi
  DOUBLE PRECISION :: ampl_st,a_st,p_st,b_st,c_st
  DOUBLE PRECISION :: a_ellipcoll, beta_ellipcoll, alpha_ellipcoll, norm_ellipcoll
  DOUBLE PRECISION :: r, dumh

  DOUBLE PRECISION, PARAMETER :: rho_c=2.7755d11

  DOUBLE PRECISION :: om_m,om_l,om_r,om_b
  DOUBLE PRECISION :: h100
  DOUBLE PRECISION :: s8
  DOUBLE PRECISION :: gamma
  DOUBLE PRECISION :: delta_c
  DOUBLE PRECISION :: Y  

  DOUBLE PRECISION :: n_s,k0,dn_dlnk
  double precision :: k_smooth


  
CONTAINS

  DOUBLE PRECISION FUNCTION sigmasq(x)

    USE nrint, ONLY : qromb
    IMPLICIT NONE

    DOUBLE PRECISION, INTENT(in) :: x
    DOUBLE PRECISION :: lnkmin, lnkmax, res
    DOUBLE PRECISION, PARAMETER :: eps = 1.d-6

    r = x
    lnkmin = -6.90
    IF (r == 0.d0) THEN
       lnkmax = LOG(1.d5)
    ELSE
       lnkmax = LOG(10.90410 / r)
    END IF
    res = qromb(integrand_sigmasq, lnkmin, lnkmax, eps)

    !PRINT *,x
    !IF (ifail.NE.0) STOP 'sigmasq'
    sigmasq = res / (2.d0*pi*pi)
  END FUNCTION sigmasq

  FUNCTION integrand_sigmasq(lnk)
    IMPLICIT NONE

    DOUBLE PRECISION, DIMENSION(:), INTENT(in) :: lnk
    DOUBLE PRECISION, DIMENSION(SIZE(lnk)) :: integrand_sigmasq
    DOUBLE PRECISION :: k
    INTEGER :: i, n

    n=SIZE(lnk)
    DO i=1,n
       k = EXP(lnk(i))
       integrand_sigmasq(i) = window(k * r) * k * k * k * pspec(k)
    END DO

  END FUNCTION integrand_sigmasq

    DOUBLE PRECISION FUNCTION probdist(nu)

    IMPLICIT NONE

    DOUBLE PRECISION, INTENT(in) :: nu
    DOUBLE PRECISION :: k

    k=SQRT(2.d0/pi)
    probdist=k*EXP(-nu*nu/2.d0)
  END FUNCTION probdist



  DOUBLE PRECISION FUNCTION sigma(x)
    IMPLICIT NONE
    DOUBLE PRECISION, INTENT(in) :: x

    sigma=SQRT(sigmasq(x))
  END FUNCTION sigma


  DOUBLE PRECISION FUNCTION logsigma(logx)

    IMPLICIT NONE
    DOUBLE PRECISION, INTENT(in) :: logx
    DOUBLE PRECISION :: x

    x=EXP(logx)
    logsigma=LOG(sigma(x))

  END FUNCTION logsigma

  FUNCTION dfridr(func,x,h,err)
    IMPLICIT NONE

    DOUBLE PRECISION, INTENT(in) :: x,h
    DOUBLE PRECISION, INTENT(out) :: err
    DOUBLE PRECISION :: dfridr
    INTERFACE
       FUNCTION func(x)
         DOUBLE PRECISION, intent(in) :: x
         DOUBLE PRECISION :: func
       END FUNCTION func
    END INTERFACE
    EXTERNAL :: func


    INTEGER, parameter :: NTAB=10
    DOUBLE PRECISION, PARAMETER :: CON=1.4d0,CON2=CON*CON,BIG=1.d30,SAFE=2.d0
    INTEGER :: ierrmin,i,j
    INTEGER, DIMENSION(1) :: imin
    DOUBLE PRECISION :: hh
    DOUBLE PRECISION, DIMENSION(NTAB-1) :: errt,fac
    DOUBLE PRECISION, DIMENSION(NTAB,NTAB) :: a

    IF(h.EQ.0.) STOP 'h must be nonzero in dfridr'
    hh=h
    a(1,1)=(func(x+hh)-func(x-hh))/(2.d0*hh)
    err=BIG
    fac(1)=CON
    DO i=2,NTAB-1
       fac(i)=fac(i-1)*CON
    ENDDO
    DO i=2,NTAB
       hh=hh/CON
       a(1,i)=(func(x+hh)-func(x-hh))/(2.d0*hh)
       DO j=2,i
          a(j,i)=(a(j-1,i)*fac(j-1)-a(j-1,i-1))/(fac(j-1)-1.d0)
       ENDDO
       errt(1:i-1)=MAX(ABS(a(2:i,i)-a(1:i-1,i)),ABS(a(2:i,i)-a(1:i-1,i-1)))
       imin=MINLOC(errt(1:i-1))
       ierrmin=imin(1)
       IF (errt(ierrmin).LE.err) THEN
          err=errt(ierrmin)
          dfridr=a(1+ierrmin,i)
       ENDIF
       IF(ABS(a(i,i)-a(i-1,i-1)).GE.SAFE*err) RETURN
    ENDDO
  END FUNCTION dfridr

  DOUBLE PRECISION FUNCTION hubbledist(z)

    IMPLICIT NONE

    DOUBLE PRECISION, INTENT(in) :: z
    DOUBLE PRECISION :: omega_k

    omega_k=1.d0-(om_l+om_m+om_r)
    hubbledist=1.d0/SQRT(omega_k*(1.d0+z)**2+om_m*(1.d0+z)**3+&
         &om_r*(1.d0+z)**4+om_l)

  END FUNCTION hubbledist


  DOUBLE PRECISION FUNCTION D(z)

    IMPLICIT NONE

    DOUBLE PRECISION, INTENT(in) :: z

    DOUBLE PRECISION :: a_upper, a_lower, dlna, integral, ai, hdist, dz, d0
    INTEGER ::  num, i


    a_upper = 1.d0 / (1.d0 + z)
    a_lower = 1.d-8
    num = 10000
    dlna = (LOG(a_upper) - LOG(a_lower)) / DBLE(num - 1)

    integral = 0.d0
    DO i = 1, num
       ai = EXP(DBLE(i-1) * dlna + LOG(a_lower))
       hdist = hubbledist(1.d0/ai - 1)
       integral = integral + hdist ** 3 / ai ** 2
    END DO
    dz = (1.d0 / hubbledist(z)) * dlna * integral

    a_upper = 1.d0
    a_lower = 1.d-8
    num = 10000
    dlna = (LOG(a_upper) - LOG(a_lower)) / DBLE(num - 1)

    integral = 0.d0
    DO i = 1, num
       ai = EXP(DBLE(i-1) * dlna + LOG(a_lower))
       hdist = hubbledist(1.d0/ai - 1)
       integral = integral + hdist ** 3 / ai ** 2
    END DO
    d0 = (1.d0 / hubbledist(0.d0)) * dlna * integral

    D = dz / d0

  END FUNCTION D


!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!11
!!!!! ELLIPSOIDAL COLLAPSE
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

  DOUBLE PRECISION FUNCTION numdenx_ellipcoll(x,z)
    IMPLICIT NONE
    DOUBLE PRECISION, INTENT(in) :: x,z
    DOUBLE PRECISION :: sig,dlogsigmadlogx,step,err,nu0,nu1,series
    DOUBLE PRECISION, PARAMETER :: pi=3.14159265358979324d0

    sig=sigma(x)
    step=0.1d0
    DO
       dlogsigmadlogx=dfridr(logsigma,LOG(x),step,err)
       IF (ABS(err).LT.1.d-5) exit
       step=step/2.d0
    END DO

    nu0 = SQRT(a_ellipcoll) * delta_c / (d(z) * sig)
    nu1 = nu0 * (1.d0 + beta_ellipcoll / nu0 ** (2 * alpha_ellipcoll))  
    series = 1.d0 - alpha_ellipcoll +&
         & alpha_ellipcoll * (alpha_ellipcoll - 1.d0) / 2.d0 -&
         & alpha_ellipcoll * (alpha_ellipcoll - 1.d0) * (alpha_ellipcoll - 2.d0) / 6.d0 +&
         & alpha_ellipcoll * (alpha_ellipcoll - 1.d0) * (alpha_ellipcoll - 2.d0)  * (alpha_ellipcoll - 3.d0) / 24.d0 -&
         & alpha_ellipcoll * (alpha_ellipcoll - 1.d0) * (alpha_ellipcoll - 2.d0)  * (alpha_ellipcoll - 3.d0)  * (alpha_ellipcoll - 4.d0) / 120.d0
    numdenx_ellipcoll = - probdist(nu1) * (3.d0/(4.d0*pi*x**3)) * dlogsigmadlogx * nu0 / x
    numdenx_ellipcoll = numdenx_ellipcoll * (1.d0 + beta_ellipcoll / nu0 ** (2.0*alpha_ellipcoll) * series)
    numdenx_ellipcoll = numdenx_ellipcoll * norm_ellipcoll

  END FUNCTION numdenx_ellipcoll


  DOUBLE PRECISION FUNCTION numdenm_ellipcoll(m,z)

    IMPLICIT NONE
    DOUBLE PRECISION, INTENT(in) :: m,z
    DOUBLE PRECISION :: x,rho_0
    DOUBLE PRECISION, PARAMETER :: pi=3.14159265358979324d0

    rho_0=rho_c*h100*h100*om_m
    x=3.d0*m/(4.d0*pi*rho_0)
    x=x**(1./3.)
    numdenm_ellipcoll=numdenx_ellipcoll(x,z)/(4.d0*pi*x*x*rho_0)

  END FUNCTION numdenm_ellipcoll

  DOUBLE PRECISION FUNCTION massfrac_ellipcoll(m,z)

    IMPLICIT NONE
    DOUBLE PRECISION, INTENT(in) :: m,z
    DOUBLE PRECISION :: rho_0

    rho_0=rho_c*h100*h100*om_m
    massfrac_ellipcoll=m*numdenm_ellipcoll(m,z)/rho_0

  END FUNCTION massfrac_ellipcoll

  DOUBLE PRECISION FUNCTION conditional_dNdlnm_ellipcoll(m_small, M_big, delta, Dz, anorm_sqrt)
    IMPLICIT NONE
    DOUBLE PRECISION, INTENT(in) :: m_small, M_big, delta, Dz, anorm_sqrt
    DOUBLE PRECISION :: x_small, X_big, s_small, S_big, rho_0
    DOUBLE PRECISION :: step, err, dlogsigmadlogx, dlogsigmadlogm
    DOUBLE PRECISION :: delta_prime, delta_0, T_series, B_s, fact, res
    DOUBLE PRECISION, PARAMETER :: pi=3.14159265358979324d0

    IF (m_small >= M_big) THEN
       conditional_dNdlnm_ellipcoll = 0.d0
       RETURN
    END IF

    rho_0 = rho_c * h100 * h100 * om_m

    x_small = 3.d0 * m_small / (4.d0 * pi * rho_0)
    x_small = x_small ** (1./3.)
    X_big = 3.d0 * M_big / (4.d0 * pi * rho_0)
    X_big = X_big ** (1./3.)

    s_small = sigma(x_small) * anorm_sqrt
    s_small = s_small ** 2
    IF (M_big > 1.d18) THEN
       S_big = 0.d0
    ELSE
       S_big = sigma(X_big) * anorm_sqrt
       S_big = S_big ** 2
    END IF


    step = 0.1d0
    DO
       dlogsigmadlogx=dfridr(logsigma,LOG(x_small),step,err)
       IF (ABS(err).LT.1.d-5) exit
       step=step/2.d0
    END DO
    dlogsigmadlogm = dlogsigmadlogx / 3.d0

    delta_0 = delta / Dz

    delta_prime = SQRT(a_ellipcoll) * delta_c * anorm_sqrt / Dz
    B_s = delta_prime * (1.d0 + beta_ellipcoll * (s_small / delta_prime ** 2) ** alpha_ellipcoll)
    fact = beta_ellipcoll * delta_prime ** (1.0 - 2.0 * alpha_ellipcoll)
    T_series = B_s - delta_0 + &
         & (S_big - s_small) * alpha_ellipcoll * fact * s_small ** (alpha_ellipcoll - 1.0) + &
         & ( (S_big - s_small) ** 2 / 2.d0) * alpha_ellipcoll * (alpha_ellipcoll - 1.d0) * fact * s_small ** (alpha_ellipcoll - 2.0) + &
         & ( (S_big - s_small) ** 3 / 6.d0) * alpha_ellipcoll * (alpha_ellipcoll - 1.d0) * (alpha_ellipcoll - 2.d0) * fact * s_small ** (alpha_ellipcoll - 3.0) + &
         & ( (S_big - s_small) ** 4 / 24.d0) * alpha_ellipcoll * (alpha_ellipcoll - 1.d0) * (alpha_ellipcoll - 2.d0) * (alpha_ellipcoll - 3.d0) * fact * s_small ** (alpha_ellipcoll - 4.0) + &
         & ( (S_big - s_small) ** 5 / 120.d0) * alpha_ellipcoll * (alpha_ellipcoll - 1.d0) * (alpha_ellipcoll - 2.d0) * (alpha_ellipcoll - 3.d0) * (alpha_ellipcoll - 4.d0) * fact * s_small ** (alpha_ellipcoll - 5.0)
    T_series = ABS(T_series)

    res = (M_big / m_small) * 2 * T_series * s_small / SQRT(2.d0 * pi * (s_small - S_big) ** 3) * EXP(- 0.5d0 * (B_s - delta_0) ** 2 / (s_small - S_big)) * ABS(dlogsigmadlogm)
    conditional_dNdlnm_ellipcoll = res * norm_ellipcoll

    RETURN
  END FUNCTION conditional_dNdlnm_ellipcoll

  SUBROUTINE cumul_conditional_num_ellipcoll(m_small, M_big, delta, z, anorm_sqrt, res)
    IMPLICIT NONE
    DOUBLE PRECISION, DIMENSION(:), INTENT(in) :: m_small
    DOUBLE PRECISION, INTENT(in) :: M_big, delta, z, anorm_sqrt
    DOUBLE PRECISION, DIMENSION(:), INTENT(out) :: res

    DOUBLE PRECISION, DIMENSION(:), ALLOCATABLE :: dNdlnm
    INTEGER :: n, i
    DOUBLE PRECISION :: dlnm, totnum

    n = SIZE(m_small)
    dlnm = (LOG(m_small(n)) - LOG(m_small(1))) / DBLE(n-1)
    !PRINT *, dlnm, LOG(m_small(2)) - LOG(m_small(1))

    ALLOCATE(dNdlnm(n))
    res = 0.d0
    DO i = 1, n
       dNdlnm(i) = conditional_dNdlnm_ellipcoll(m_small(i), M_big, delta, z, anorm_sqrt)
       IF (i == 1) THEN
          res(i) = dNdlnm(i) * dlnm
       ELSEIF (i > 1) THEN
          res(i) = res(i-1) + dNdlnm(i) * dlnm
       END IF
    END DO
    totnum = res(n)
    DO i=1,n
       res(i) = totnum - res(i)
    END DO

  END SUBROUTINE cumul_conditional_num_ellipcoll

  DOUBLE PRECISION FUNCTION pspec(k)
    IMPLICIT NONE

    DOUBLE PRECISION, INTENT(in) :: k
    DOUBLE PRECISION :: kbyh,tfun,pspecdm3d,pspec_EH,n0

    pspec=0.d0

    if (k < 0.0) return
    kbyh = k / h100

    IF (dn_dlnk == 0.0) THEN
       n0=n_s
    ELSE
       n0=n_s+0.50*dn_dlnk*LOG(k/k0)
    END IF

    tfun=transfun_EH(kbyh)
    pspecdm3d=(k**n0)*tfun*tfun
    pspec_EH=pspecdm3d
    IF ((k_smooth < 1.d3).AND.(k_smooth > 1.d-8)) pspec_EH=pspec_EH*EXP(-k*k/(k_smooth*k_smooth))
    !pspec_EH=norm*EXP(-((k-5.0)/1.0)**2)+EXP(-((k-15.0)/1.0)**2)

    pspec=pspec_EH


  END FUNCTION pspec

  FUNCTION transfun_EH(k)

    IMPLICIT NONE

    DOUBLE PRECISION, INTENT(in) :: k
    DOUBLE PRECISION :: transfun_EH
    DOUBLE PRECISION :: hubble,ombh2,theta,s,ommh2,a,q,L0,C0,tmp

    hubble = h100

    ombh2 = om_b * hubble * hubble

    theta = 2.728 / 2.7
    ommh2 = om_m * hubble * hubble
    s = 44.5 * log(9.83 / ommh2) / sqrt(1. + 10. * exp(0.75 * log(ombh2))) * hubble
    a = 1. - 0.328 * log(431. * ommh2) * ombh2 / ommh2 + 0.380 * log(22.3 * ommh2) * (ombh2 / ommh2) * (ombh2 / ommh2)
    gamma = a + (1. - a) / (1. + exp(4 * log(0.43 * k * s)))
    gamma = gamma * om_m * hubble
    q = k * theta * theta / gamma
    L0 = log(2. * exp(1.) + 1.8 * q)
    C0 = 14.2 + 731. / (1. + 62.5 * q)
    tmp = L0 / (L0 + C0 * q * q)

    transfun_EH=tmp

  END FUNCTION transfun_EH

  DOUBLE PRECISION FUNCTION norm(sig)

    USE nrint, ONLY : qromb
    IMPLICIT NONE

    DOUBLE PRECISION, INTENT(in) :: sig
    DOUBLE PRECISION :: lnkmin, lnkmax, res
    DOUBLE PRECISION, PARAMETER :: eps = 1.d-6


    r = 8.d0 / h100

    lnkmin = -6.9d0
    lnkmax = LOG(10.9041d0 / r)
    res = qromb(integrand_sigmasq, lnkmin, lnkmax, eps)

    norm=sig * sig * two_pi * pi / res

  END FUNCTION norm


  FUNCTION window(x)
    IMPLICIT NONE

    DOUBLE PRECISION, INTENT(in) :: x
    DOUBLE PRECISION :: window

    IF (x == 0.d0) THEN
       window = 1.d0!-x*x/10.0
    ELSEIF (x > 10.9041d0) THEN
       window = 0.d0
    ELSE
       window = 3.d0 * ((SIN(x) / x**3) - (COS(x) / x**2))
    END IF
    window = window * window

  END FUNCTION window


END MODULE fcoll_grid


