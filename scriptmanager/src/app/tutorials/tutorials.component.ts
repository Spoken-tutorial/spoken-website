import { Component, OnInit } from '@angular/core';
import {ApiService } from '../api.service';

@Component({
  selector: 'app-tutorials',
  templateUrl: './tutorials.component.html',
  styleUrls: ['./tutorials.component.scss']
})
export class TutorialsComponent implements OnInit {

  public Foss ;

  constructor(public apiService: ApiService){
     this.Foss = this.apiService.getFoss();
    // console.log(Foss);
  }

  fossCategorySelected(category){
    console.log(category);
  }
  
  ngOnInit(){}
//   ngOnInit(){
//     this.apiService.getCustomers().subscribe((res)=>{
//       this.apiService.getCustomers().subscribe((res)=>{
//         console.log(res);
//       });      
//     });
// }

}
