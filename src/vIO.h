#ifndef VIO_H_INCLUDED
#define VIO_H_INCLUDED

#include "Std_Types.h"


typedef void (*vfls_init)           (void);
typedef int  (*vfls_write)          (int, int);
typedef int  (*vfls_erase)          (int, int);
typedef int  (*vfls_get_status)     (void);
typedef int  (*vfls_get_job_result) (void);
typedef void (*vfls_cancel)         (void);
typedef int  (*vfls_read)           (int, uint8*, int);
typedef void (*vfls_set_mode)       (int);


extern vfls_init            vFls_Init;
extern vfls_write           vFls_Write;
extern vfls_erase           vFls_Erase;
extern vfls_get_status      vFls_GetStatus;
extern vfls_get_job_result  vFls_GetJobResult;
extern vfls_cancel          vFls_Cancel;
extern vfls_read            vFls_Read;
extern vfls_set_mode        vFls_SetMode;

int vio_initialize(void);
int vFls_Init_Wr_Callback(vfls_write callback);


#endif /* VIO_H_INCLUDED */
