using System;
using System.Text;
using System.Windows.Forms;
using Script.Methods;
public partial class UserScript:ScriptMethods,IProcessMethods
{
    //the count of process
	//执行次数计数
    int processCount ;  
    string[] EWM_result={};
    string EWM_dat;
    /// <summary>
    /// Initialize the field's value when compiling
	/// 预编译时变量初始化
    /// </summary>
    public void Init()
    {
        //You can add other global fields here
		//变量初始化，其余变量可在该函数中添加
        processCount = 0;
        EWM_dat=null;
       
    }

    /// <summary>
    /// Enter the process function when running code once
	/// 流程执行一次进入Process函数
    /// </summary>
    /// <returns></returns>
    public bool Process()
    {
        //You can add your codes here, for realizing your desired function
		//每次执行将进入该函数，此处添加所需的逻辑流程处理
        //MessageBox.Show("Process Success");
        EWM_dat=EWM;
        EWM_dat=EWM_dat.Substring(1,EWM_dat.Length-2);
        EWM_result=EWM_dat.Split(new char[2]{';',','});
        E1=EWM_result[0];
        E2=EWM_result[1];
        E3=EWM_result[2];
        E4=EWM_result[3];
        return true;
    }
}
                            