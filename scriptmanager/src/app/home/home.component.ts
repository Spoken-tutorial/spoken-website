import { Component, OnInit } from '@angular/core';
import { FossService } from '../_service/foss.service';
import { TutorialsService } from '../_service/tutorials.service'

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.sass']
})
export class HomeComponent implements OnInit {

  public foss;
  public tutorials;
  public fid;
  constructor(public fossService: FossService,public tutorialService: TutorialsService){}


  LanguageSelected(language){
    console.log(language);
  }
  
  fetchAllTutorials(fid){
    console.log(fid)
   if(fid!='all')
      fid = 83;
   this.fid = fid;

     this.tutorialService.getTutorials(this.fid).subscribe(
      (res) => this.tutorials = res,
      (err) => {
        console.log('Failed to fetch foss categories');
        console.error(err);
      }
    );
    
  }

  fetchAllFoss(){
     this.fossService.getFoss().subscribe(
      (res) => this.foss = res,
      (err) => {
        console.log('Failed to fetch foss categories');
        console.error(err);
      }
    );
  }

  ngOnInit(){
    this.fetchAllFoss();
    this.fetchAllTutorials('all');
  
  };

}
